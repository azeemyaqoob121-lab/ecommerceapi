"""
Wrapper script to run the test suite
"""
import subprocess
import sys

if __name__ == '__main__':
    print("Running E-Commerce API Tests...\n")
    result = subprocess.run([sys.executable, 'scripts/test_api.py'], capture_output=False)
    sys.exit(result.returncode)
