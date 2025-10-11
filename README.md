# Portfolio CLI (orange-cli)

A command-line portfolio & investment manager with:
- Admin/user login
- User management (admin only)
- Portfolios (create/view/delete)
- Marketplace (multi-ticker buy)
- Sell/liquidate
- Pretty tables via `rich`
- Local persistence between runs

## Requirements
- Python 3.10+ (tested with 3.12)
- macOS/Linux/Windows

## Setup

```bash
git clone <YOUR_REPO_URL>.git
cd orange-cli-1

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
