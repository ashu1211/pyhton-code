import os
import subprocess
import boto3
from botocore.exceptions import NoCredentialsError

# Set AWS SES credentials and region
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIA6GVE********************'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'EH6pCZca0C2msVRLn4**********'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Sender and recipient email addresses
sender = "alert@instanodes.io"
recipient = "kumar.ashwani@antiersolutions.com,mmashwani22@gmail.com"

# Base directory where the repositories should be cloned
base_dir = "/home/ant/nodes"

# Repository details
repos = {
    "Blockbook": "https://github.com/trezor/blockbook",
    "Ethereum": "https://github.com/ethereum/go-ethereum.git",
    "Prysm": "https://github.com/prysmaticlabs/prysm.git",
    "Bitcoin": "https://github.com/bitcoin/bitcoin.git",
    "Litecoin": "https://github.com/litecoin-project/litecoin.git",
    "BSC": "https://github.com/bnb-chain/bsc.git",
    "Heimdalld": "https://github.com/maticnetwork/heimdall.git",
    "Bor": "https://github.com/maticnetwork/bor.git",
    "Tron": "https://github.com/tronprotocol/java-tron.git",
    "Tezos": "https://github.com/tezos/tezos-mirror.git",
    "Polkadot": "https://github.com/paritytech/polkadot",
    "Stellar-horizon": "https://github.com/stellar/go",
    "Stellar-core": "https://github.com/stellar/stellar-core",
    "Arbitrum": "https://github.com/OffchainLabs/nitro",
    "TON": "https://github.com/ton-blockchain/ton",
    "Corda": "https://github.com/corda/corda"
}
# Initialize SES client
ses_client = boto3.client('ses', region_name=os.environ['AWS_DEFAULT_REGION'])

def send_email(subject, body):
    try:
        response = ses_client.send_email(
            Source=sender,
            Destination={
                'ToAddresses': [recipient]
            },
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        print("Email sent! Message ID:", response['MessageId'])
    except NoCredentialsError:
        print("Credentials not available")

def get_latest_tag(repo_path):
    result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], cwd=repo_path, capture_output=True, text=True)
    return result.stdout.strip()

def check_and_update_repo(repo_name, repo_url):
    repo_path = os.path.join(base_dir, repo_name)

    if not os.path.isdir(repo_path):
        print(f"Cloning the {repo_name} repository...")
        subprocess.run(['git', 'clone', repo_url, repo_path])
    else:
        print(f"{repo_name} directory already exists.")

    current_tag = get_latest_tag(repo_path)

    subprocess.run(['git', 'pull', 'origin'], cwd=repo_path)

    updated_tag = get_latest_tag(repo_path)

    if current_tag != updated_tag:
        print(f"Git tag changed from {current_tag} to {updated_tag}. Triggering email alert.")
        email_subject = f"{repo_name} Version Update Alert"
        email_body = f"Git tag changed from {current_tag} to {updated_tag} in {repo_name} repository."
        send_email(email_subject, email_body)
    else:
        print("No important updates found.")

def main():
    os.makedirs(base_dir, exist_ok=True)
    os.chdir(base_dir)

    for repo_name, repo_url in repos.items():
        check_and_update_repo(repo_name, repo_url)

if __name__ == "__main__":
    main()
