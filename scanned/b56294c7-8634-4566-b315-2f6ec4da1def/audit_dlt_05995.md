# [?] fix: crash in mnemonicverificationdialog by proper using reject() event

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-02
Source: https://github.com/dashpay/dash/commit/c24473b99d698b7a4c75b70f5b833824c5e23e96
Type: security-commit

## Details
fix: crash in mnemonicverificationdialog by proper using reject() event

This call disconnect(cancel, nullptr, nullptr, nullptr) for cancel makes
an internal slots disconnected and it could cause objects to get
invalid internal state at some point if theme is changed.

## Patch
### src/qt/forms/mnemonicverificationdialog.ui
```diff
@@ -156,24 +156,6 @@
          </item>
         </layout>
        </item>
-       <item>
-        <layout class="QHBoxLayout" name="horizontalLayout_actions">
-         <item>
-          <widget class="QPushButton" name="showMnemonicAgainButton">
-           <property name="text">
-            <string>Back</string>
-           </property>
-          </widget>
-         </item>
-         <item>
-          <spacer name="horizontalSpacer_2">
-           <property name="orientation">
-            <enum>Qt::Horizontal</enum>
-           </property>
-          </spacer>
-         </item>
-        </layout>
-       </item>
       </layout>
      </widget>
     </widget>
```

### src/qt/mnemonicverificationdialog.cpp
```diff
@@ -87,7 +87,6 @@ MnemonicVerificationDialog::MnemonicVerificationDialog(const SecureString& mnemo
         connect(ui->word1Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord1Changed);
         connect(ui->word2Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord2Changed);
         connect(ui->word3Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord3Changed);
-        connect(ui->showMnemonicAgainButton, &QPushButton::clicked, this, &MnemonicVerificationDialog::onShowMnemonicAgainClicked);
     }
 
     // Button box
@@ -206,13 +205,9 @@ void MnemonicVerificationDialog::setupStep2()
 
     ui->buttonBox->show();
     if (QAbstractButton* cancel = ui->buttonBox->button(QDialogButtonBox::Cancel)) {
-        cancel->show();
         cancel->setText(tr("Back"));
-        disconnect(cancel, nullptr, nullptr, nullptr);
-        connect(cancel, &QAbstractButton::clicked, this, &MnemonicVerificationDialog::onShowMnemonicAgainClicked);
     }
     if (QAbstractButton* cont = ui->buttonBox->button(QDialogButtonBox::Ok)) cont->setEnabled(false);
-    if (ui->showMnemonicAgainButton) ui->showMnemonicAgainButton->hide();
 
     // Verification label styling is defined in general.css
 
@@ -290,7 +285,7 @@ void MnemonicVerificationDialog::onHideMnemonicClicked()
     clearWordsSecurely();
 }
 
-void MnemonicVerificationDialog::onShowMnemonicAgainClicked()
+void MnemonicVerificationDialog::reject()
 {
     // Clear words when going back to step 1 (unless mnemonic is revealed)
     if (!m_mnemonic_revealed) {
```

### src/qt/mnemonicverificationdialog.h
```diff
@@ -24,15 +24,16 @@ class MnemonicVerificationDialog : public QDialog
     explicit MnemonicVerificationDialog(const SecureString& mnemonic, QWidget *parent = nullptr, bool viewOnly = false);
     ~MnemonicVerificationDialog();
 
+protected:
     void accept() override;
+    void reject() override;
 
 private Q_SLOTS:
     void onShowMnemonicClicked();
     void onHideMnemonicClicked();
     void onWord1Changed();
     void onWord2Changed();
     void onWord3Changed();
-    void onShowMnemonicAgainClicked();
 
 private:
     void setupStep1();
```
