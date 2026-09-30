# [?] Merge #7126: fix: crash when theme is changed if mnemonic dialog has been shown

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-06
Source: https://github.com/dashpay/dash/commit/7d0d5a7ea7ab6c71c47f048f58fa7cfe6b072509
Type: security-commit

## Details
Merge #7126: fix: crash when theme is changed if mnemonic dialog has been shown

009104c35916c02e89605ddde6375711851ec879 fix: return full functionality of Back / Cancel button on mnemonic verification dialog (Konstantin Akimov)
c24473b99d698b7a4c75b70f5b833824c5e23e96 fix: crash in mnemonicverificationdialog by proper using reject() event (Konstantin Akimov)

Pull request description:

  ## Issue being fixed or feature implemented
  First found by thepez while testing https://github.com/dashpay/dash/pull/7040

  It happens every time when create new wallet after dialog to validate mnemonic has been shown.

  Steps to reproduce:
   1. Create new wallet
   2. Show mnemonic
   3. Confirm the mnemonic is saved
   4. Close dialog by Canceling validation or by Confirming validation
   5. Change theme crashes app

  ```
      2025-12-22T15:16:31Z Posix Signal: Segmentation fault
      0#: (0x608F5BE3FDB5) stl_vector.h:115         - std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data::_M_copy_data(std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data const&)
       1#: (0x608F5BE3FDB5) stl_vector.h:127         - std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data::_M_swap_data(std::_Vector_base<unsigned long, std::allocator<unsigned long> >::_Vector_impl_data&)
       2#: (0x608F5BE3FDB5) stl_vector.h:1962        - std::vector<unsigned long, std::allocator<unsigned long> >::_M_move_assign(std::vector<unsigned long, std::allocator<unsigned long> >&&, std::integral_constant<bool, true>)
       3#: (0x608F5BE3FDB5) stl_vector.h:771         - std::vector<unsigned long, std::allocator<unsigned long> >::operator=(std::vector<unsigned long, std::allocator<unsigned long> >&&)
       4#: (0x608F5BE3FDB5) stacktraces.cpp:784      - HandlePosixSignal
       5#: (0x7D6B37A45330) libc_sigaction.c         - ???
       6#: (0x608F5CC0951B) <unknown-file>           - ???
       7#: (0x608F5CC09901) <unknown-file>           - ???
       8#: (0x608F5B62369D) unique_lock.h:105        - std::unique_lock<std::recursive_mutex>::~unique_lock()
       9#: (0x608F5B62369D) sync.h:226               - UniqueLock<AnnotatedMixin<std::recursive_mutex> >::~UniqueLock()
      10#: (0x608F5B62369D) guiutil.cpp:1031         - GUIUtil::loadStyleSheet(bool)
      11#: (0x608F5B6243C4) guiutil.cpp:1616         - GUIUtil::loadTheme(bool)
      12#: (0x608F5B6C27B7) atomic_base.h:505        - std::__atomic_base<int>::load(std::memory_order) const
      13#: (0x608F5B6C27B7) qatomic_cxx11.h:239      - int QAtomicOps<int>::loadRelaxed<int>(std::atomic<int> const&)
      14#: (0x608F5B6C27B7) qbasicatomic.h:107       - QBasicAtomicInteger<int>::loadRelaxed() const
      15#: (0x608F5B6C27B7) qrefcount.h:66           - QtPrivate::RefCount::deref()
      16#: (0x608F5B6C27B7) qstring.h:1308           - QString::~QString()
      17#: (0x608F5B6C27B7) appearancewidget.cpp:110 - AppearanceWidget::updateTheme(QString const&)
      18#: (0x608F5C90A0CD) <unknown-file>           - ???
      19#: (0x608F5CC5B1E1) <unknown-file>           - ???
      20#: (0x608F5CC5D00B) <unknown-file>           - ???
      21#: (0x608F5CC5D29B) <unknown-file>           - ???
      22#: (0x608F5C90A2EB) <unknown-file>           - ???
      23#: (0x608F5CC57376) <unknown-file>           - ???
      24#: (0x608F5CC586F6) <unknown-file>           - ???
      25#: (0x608F5C8DD693) <unknown-file>           - ???
  ```

  Current call `disconnect(cancel, nullptr, nullptr, nullptr)` is too violent for qt objects because it disconnects not only user-added slots, but internal qt slots too; it makes the object _Cancel Button_ to be in an invalid state.

  ## What was done?
  Easiest fix is specify _some_ arguments for disconnect, for example, simple `disconnect(cancel, &QDialogButtonBox::rejected, this, nullptr);` fixes crash but it breaks functionality of Cancel button.

  For the final solution look to the commits in PR

  ## How Has This Been Tested?

  Tested numerous user cases (list is not full):
   - create wallet, validate mnemonic, click "BACK"
   - create wallet, close dialog without validation mnemonic
   - create wallet, validate mnemonic, click BACK, re-validate mnemonic
   - show mnemonic for already existing wallet

  Also I tried to do the exactly same things, but instead mouse's click use Escape or Ctrl+W or close window by mouse.

  I am not sure that I provided 100% coverage by manual testing, but at this point it looks solid for me. Any extra testing is welcome, please help with it!

  ## Breaking Changes
  N/A

  ## Checklist:
  - [x] I have performed a self-review of my own code
  - [ ] I have commented my code, particularly in hard-to-understand areas
  - [ ] I have added or updated relevant unit/integration/functional/e2e tests
  - [ ] I have made corresponding changes to the documentation
  - [x] I have assigned this pull request to a milestone _(for repository code-owners and collaborators only)

ACKs for top commit:
  UdjinM6:
    ACK 009104c35916c02e89605ddde6375711851ec879

Tree-SHA512: aab64388dcc90b0bd2ab035fc11f0b53c55643dcf3ed6c0859ba2ce3865d8341243892e56fc998391652b9da11be815360c80314c24c6cea90a896196a29f9ae

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
@@ -87,14 +87,10 @@ MnemonicVerificationDialog::MnemonicVerificationDialog(const SecureString& mnemo
         connect(ui->word1Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord1Changed);
         connect(ui->word2Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord2Changed);
         connect(ui->word3Edit, &QLineEdit::textChanged, this, &MnemonicVerificationDialog::onWord3Changed);
-        connect(ui->showMnemonicAgainButton, &QPushButton::clicked, this, &MnemonicVerificationDialog::onShowMnemonicAgainClicked);
     }
 
     // Button box
     ui->buttonBox->button(QDialogButtonBox::Ok)->setText(m_view_only ? tr("Close") : tr("Continue"));
-    connect(ui->buttonBox, &QDialogButtonBox::accepted, this, &MnemonicVerificationDialog::accept);
-    connect(ui->buttonBox, &QDialogButtonBox::rejected, this, &MnemonicVerificationDialog::reject);
-
     GUIUtil::handleCloseWindowShortcut(this);
 }
 
@@ -206,13 +202,9 @@ void MnemonicVerificationDialog::setupStep2()
 
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
 
@@ -290,13 +282,18 @@ void MnemonicVerificationDialog::onHideMnemonicClicked()
     clearWordsSecurely();
 }
 
-void MnemonicVerificationDialog::onShowMnemonicAgainClicked()
+void MnemonicVerificationDialog::reject()
 {
     // Clear words when going back to step 1 (unless mnemonic is revealed)
     if (!m_mnemonic_revealed) {
         clearWordsSecurely();
     }
-    setupStep1();
+    // close dialog for step-1; return back to step-1 for step-2
+    if (ui->stackedWidget->currentIndex() == 0) {
+        QDialog::reject();
+    } else {
+        setupStep1();
+    }
 }
 
 void MnemonicVerificationDialog::onWord1Changed() { updateWordValidation(); }
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
