import subprocess
import logging
import psutil

logger = logging.getLogger()

class ClientManager:
    def check_vcan(self, local_channel):
        try:
            # Check if vcan0 is listed among network interfaces
            result = subprocess.run(["ip", "link", "show", str(local_channel)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Error checking vcan: {e}")
            return False

    def setup_vcan(self, local_channel, local_channel_type):
        try:
            # Load the vcan kernel module
            subprocess.run(["sudo", "modprobe", str(local_channel_type)], check=True)
            # Add the vcan0 interface
            subprocess.run(["sudo", "ip", "link", "add", "dev", str(local_channel), "type", str(local_channel_type)], check=True)
            # Bring the interface up
            subprocess.run(["sudo", "ip", "link", "set", "up", str(local_channel)], check=True)
            logger.info("CAN interface set up successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set up vcan: {e}")

    def kill_process(self, process):
        try:
            parent_pid = psutil.Process(process.pid)
            children = parent_pid.children(recursive=True)
            for child_pid in children:
                child_pid.terminate()
            parent_pid.terminate()

            _, alive = psutil.wait_procs([parent_pid] + children, timeout=5)
            for pids in alive:
                pids.kill()
        except psutil.NoSuchProcess:
            logger.info("Process already terminated.")