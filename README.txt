# 1. Install Azure CLI (if not already)
winget install Microsoft.AzureCLI

# 2. Login
az login

# 3. Create the App Service (one-time)
az webapp up --name listing-generator-app --resource-group rg-listing-generator --runtime "PYTHON:3.12" --sku B1

# 4. Set environment variables (your .env values)
az webapp config appsettings set --name listing-generator-app --resource-group rg-listing-generator --settings AZURE_OPENAI_ENDPOINT="your-endpoint" AZURE_OPENAI_API_KEY="your-key" AZURE_OPENAI_API_VERSION="2024-12-01-preview" AZURE_OPENAI_DEPLOYMENT="gpt-4o"

# 5. Set startup command
az webapp config set --name listing-generator-app --resource-group rg-listing-generator --startup-file "startup.sh"
