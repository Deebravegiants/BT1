# [M] Unsafe Storage of Private Key and Mnemonic Words

## Summary
Severity: Medium
Contest weight: 0.5945
Dataset id: 12195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Possessing the private key and the mnemonic words is equivalent to having the right to dispose the asset in corresponding wallet. We performed a check about the implementation of storing private key on the iOS platform, and found out that the private key generation function createAction() invokes encryptSecretStorageJSON() (line 80). The storage of private key follows the core KeyStore standard and the eclipse encryption algorithm, which basically eliminates the possibility of brute force cracking for private keys.
```solidity
(void) createAction {
    if (![self.textFieldView.textField.text isEqualToString:KUser.localPassword]) {
        Alert *alert = [[Alert alloc] initWithTitle:LocalizedString(@"TwoPasswordInconsistent") duration:kAlertDuration completion: {
        }];
        [alert showAlert];
        return;
    }
    [MBProgressHUD showActivityMessageInView:nil];
    NSLog(@"%@ %@", KUser.localPrivateKey, KUser.localPhraseString);
    if (!IsEmpty(KUser.localPhraseString)) {
        self.account = [Account accountWithMnemonicPhrase:KUser.localPhraseString];
    } else if (!IsEmpty(KUser.localPrivateKey)) {
        SecureData *data = [SecureData secureDataWithHexString:KUser.localPrivateKey];
        self.account = [Account accountWithPrivateKey:data.data];
    } else {
        self.account = [Account randomMnemonicAccount];
    }
    [self.account encryptSecretStorageJSON:KUser.localPassword callback:^(NSString *json) {
        [self backupKeystore:json];
    }];
}
```
sqlite database, we found that model object stores not only the KeyStore data, but also the MD5 hash value of the password (line 91), private key, and mnemonic words. After we continued our analysis, we found that the private key and mnemonic words are encrypted and stored by AES(privatekey/mnemonicPhrase, password). Therefore, if the password is not very strong with complex combinations and the attacker has access to the sqlite database data, he may brute force to uncover the private key through a rainbow table attack.
```solidity
(void) backupKeystore:(NSString *)json {
    XXAccountModel *model = [[XXAccountModel alloc] init];
    model.privateKey = [AESCrypt encrypt:self.account.privateKeyString password:KUser.localPassword];
    model.publicKey = self.account.pubKey;
    model.address = self.account.BHAddress;
    model.userName = KUser.localUserName;
    model.password = [NSString md5:KUser.localPassword];
    model.keystore = json;
    if (self.account.mnemonicPhrase && IsEmpty(KUser.localPhraseString)) {
        NSString *mnemonicPhrase = [AESCrypt encrypt:self.account.mnemonicPhrase password:KUser.localPassword];
        model.mnemonicPhrase = mnemonicPhrase;
        model.backupFlag = NO;
    } else {
        model.mnemonicPhrase = @"";
        model.backupFlag = YES;
    }
    model.symbols = [NSString stringWithFormat:@"btc,eth,usdt,%@", kMainToken];
    if (KUser.accounts) {
        for (XXAccountModel *a in KUser.accounts) {
            if ([a.address isEqualToString:model.address]) {
                Alert *alert = [[Alert alloc] initWithTitle:LocalizedString(@"PrivateKeyRepetition") duration:kAlertDuration completion: {
                }];
                [alert showAlert];
                [[XXSqliteManager sharedSqlite] deleteAccountByAddress:model.address];
            }
        }
    }
    [[XXSqliteManager sharedSqlite] insertAccount:model];
    KUser.address = model.address;
    [MBProgressHUD hideHUD];
    if (model.backupFlag) {
        Alert *alert = [[Alert alloc] initWithTitle:LocalizedString(@"ImportSuccess") duration:kAlertDuration completion: {
            KWindow.rootViewController = [[XXTabBarController alloc] init];
            [self showBiometricAlert];
        }];
        [alert showAlert];
    } else {
        XXCreateWalletSuccessVC *successVC = [[XXCreateWalletSuccessVC alloc] init];
        successVC.text = KUser.localPassword;
        [self.navigationController pushViewController:successVC animated:YES];
        [self showBiometricAlert];
    }
    KUser.localPassword = @"";
    KUser.localUserName = @"";
    KUser.localPhraseString = @"";
    KUser.localPrivateKey = @"";
}
```

## Recommendation
Remove the redundant backup process as the KeyStore has stored the private key. If the backup of mnemonic words is necessary, we recommend to apply the same way by taking advantage of KeyStore.
