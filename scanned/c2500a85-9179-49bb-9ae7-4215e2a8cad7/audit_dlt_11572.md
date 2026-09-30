# [?] protocol/migrations: fix deploy.ts by avoid race condition with fs read/write

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2021-09-30
Source: https://github.com/velocity-exchange/protocol-v2/commit/8002d5b329046d6ea8232b189c60470e943cdd41
Type: security-commit

## Details
protocol/migrations: fix deploy.ts by avoid race condition with fs read/write

## Patch
### migrations/deploy.ts
```diff
@@ -122,64 +122,57 @@ async function deploy(provider: Provider) {
 	console.log('Initialized Bot for devnet');
 	await clearingHouse.unsubscribe();
 
-	await updateEnvFiles(
+	updateEnvFiles(
 		clearingHouse.program.programId,
 		mockUsdcFaucet.program.programId,
 		mockUsdcFaucetState.mint,
 		associatedTokenPublicKey
 	);
 }
 
-async function replace(filePath: string, search: RegExp, replacement: string) {
-	fs.readFile(filePath, 'utf8', function (err, data) {
-		if (err) {
-			return console.error(err);
-		}
-		const result = data.replace(search, replacement);
-
-		fs.writeFile(filePath, result, 'utf8', function (err) {
-			if (err) return console.error(err);
-		});
-	});
+function replace(filePath: string, search: RegExp, replacement: string) {
+	const data = fs.readFileSync(filePath, 'utf8');
+	const result = data.replace(search, replacement);
+	fs.writeFileSync(filePath, result, 'utf8');
 }
 
-async function updateEnvFiles(
+function updateEnvFiles(
 	clearingHouseProgramId: PublicKey,
 	mockUSDCFaucetProgramId: PublicKey,
 	USDCMintProgramId: PublicKey,
 	offChainBotTokenAccount: PublicKey
 ) {
 	const uiEnvPath = `${__dirname}/../../ui/.env`;
-	await replace(
+	replace(
 		uiEnvPath,
 		/NEXT_PUBLIC_CLEARING_HOUSE_PROGRAM_ID=([\d\w]*)/g,
 		`NEXT_PUBLIC_CLEARING_HOUSE_PROGRAM_ID=${clearingHouseProgramId.toString()}`
 	);
-	await replace(
+	replace(
 		uiEnvPath,
 		/NEXT_PUBLIC_USDC_MINT_ADDRESS=([\d\w]*)/g,
 		`NEXT_PUBLIC_USDC_MINT_ADDRESS=${USDCMintProgramId.toString()}`
 	);
-	await replace(
+	replace(
 		uiEnvPath,
 		/NEXT_PUBLIC_MOCK_USDC_FAUCET_ADDRESS=([\d\w]*)/g,
 		`NEXT_PUBLIC_MOCK_USDC_FAUCET_ADDRESS=${mockUSDCFaucetProgramId.toString()}`
 	);
 
 	const offChainBotEnvPath = `${__dirname}/../../off-chain-bot/.env`;
-	await replace(
+	replace(
 		offChainBotEnvPath,
 		/LIQUIDATION_USER_TOKEN_PUBLIC_KEY=([\d\w]*)/g,
 		`LIQUIDATION_USER_TOKEN_PUBLIC_KEY=${offChainBotTokenAccount.toString()}`
 	);
-	await replace(
+	replace(
 		offChainBotEnvPath,
-		/NEXT_PUBLIC_USDC_MINT_ADDRESS=([\d\w]*)/g,
+		/CLEARING_HOUSE_PROGRAM_ID=([\d\w]*)/g,
 		`CLEARING_HOUSE_PROGRAM_ID=${clearingHouseProgramId.toString()}`
 	);
 
 	const exchangeHistoryEnvPath = `${__dirname}/../../exchange-history/.env`;
-	await replace(
+	replace(
 		exchangeHistoryEnvPath,
 		/CLEARING_HOUSE_PROGRAM_ID=([\d\w]*)/g,
 		`CLEARING_HOUSE_PROGRAM_ID=${clearingHouseProgramId.toString()}`
```
