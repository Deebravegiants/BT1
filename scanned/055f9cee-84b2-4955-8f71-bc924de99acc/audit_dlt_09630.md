# [?] fix: avoid precision loss, storing as `CAmount`, fix potential overflow

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2026-02-11
Source: https://github.com/dashpay/dash/commit/99fd1181971b06477e25b358c95b7a2c82e8d502
Type: security-commit

## Details
fix: avoid precision loss, storing as `CAmount`, fix potential overflow

## Patch
### src/qt/proposalmodel.cpp
```diff
@@ -16,6 +16,7 @@
 #include <univalue.h>
 
 #include <algorithm>
+#include <cmath>
 
 Proposal::Proposal(ClientModel* _clientModel, const CGovernanceObject& _govObj) :
     clientModel{_clientModel},
@@ -40,7 +41,7 @@ Proposal::Proposal(ClientModel* _clientModel, const CGovernanceObject& _govObj)
     }
 
     if (const UniValue& amountValue = prop_data.find_value("payment_amount"); amountValue.isNum()) {
-        m_paymentAmount = amountValue.get_real();
+        m_paymentAmount = llround(amountValue.get_real() * COIN);
     }
 
     if (const UniValue& urlValue = prop_data.find_value("url"); urlValue.isStr()) {
@@ -121,7 +122,7 @@ QVariant ProposalModel::data(const QModelIndex& index, int role) const
         case Column::END_DATE:
             return proposal->endDate().date();
         case Column::PAYMENT_AMOUNT: {
-            return BitcoinUnits::floorWithUnit(m_display_unit, proposal->paymentAmount() * COIN, false,
+            return BitcoinUnits::floorWithUnit(m_display_unit, proposal->paymentAmount(), false,
                                                BitcoinUnits::SeparatorStyle::ALWAYS);
         }
         case Column::IS_ACTIVE:
@@ -146,7 +147,7 @@ QVariant ProposalModel::data(const QModelIndex& index, int role) const
         case Column::END_DATE:
             return proposal->endDate();
         case Column::PAYMENT_AMOUNT:
-            return proposal->paymentAmount();
+            return qlonglong(proposal->paymentAmount());
         case Column::IS_ACTIVE:
             return proposal->isActive();
         case Column::VOTING_STATUS:
```

### src/qt/proposalmodel.h
```diff
@@ -23,7 +23,7 @@ class Proposal
     ClientModel* clientModel;
     const CGovernanceObject govObj;
 
-    double m_paymentAmount{0.0};
+    CAmount m_paymentAmount{0};
     QDateTime m_endDate{};
     QDateTime m_startDate{};
     QString m_hash{};
@@ -34,7 +34,7 @@ class Proposal
     explicit Proposal(ClientModel* _clientModel, const CGovernanceObject& _govObj);
 
     bool isActive() const;
-    double paymentAmount() const { return m_paymentAmount; }
+    CAmount paymentAmount() const { return m_paymentAmount; }
     int GetAbsoluteYesCount() const;
     QDateTime endDate() const { return m_endDate; }
     QDateTime startDate() const { return m_startDate; }
```

### src/qt/proposalwizard.cpp
```diff
@@ -169,9 +169,7 @@ void ProposalWizard::buildJsonAndHex()
     QJsonObject o;
     o.insert("name", m_ui->editName->text());
     o.insert("payment_address", m_ui->editPayAddr->text());
-    const auto formatted = BitcoinUnits::format(BitcoinUnits::Unit::DASH, m_ui->paymentAmount->value(), false,
-                                                BitcoinUnits::SeparatorStyle::NEVER);
-    o.insert("payment_amount", formatted.toDouble());
+    o.insert("payment_amount", m_ui->paymentAmount->value() / static_cast<double>(COIN));
     o.insert("url", m_ui->editUrl->text());
     if (start_epoch > 0) o.insert("start_epoch", start_epoch);
     if (end_epoch > 0) o.insert("end_epoch", end_epoch);
@@ -346,11 +344,17 @@ void ProposalWizard::updateLabels()
 {
     if (m_walletModel && m_walletModel->getOptionsModel()) {
         const auto unit = m_walletModel->getOptionsModel()->getDisplayUnit();
-        const CAmount totalAmount = static_cast<CAmount>(m_ui->paymentAmount->value() *
-                                                         m_ui->comboPayments->currentData().toInt());
+        const CAmount per_payment = m_ui->paymentAmount->value();
+        const int payments = m_ui->comboPayments->currentData().toInt();
+        CAmount total{0};
+        if (payments > 0 && per_payment > 0 && per_payment <= MAX_MONEY / payments) {
+            total = per_payment * payments;
+        } else if (payments > 0 && per_payment > 0) {
+            total = MAX_MONEY;
+        }
         m_ui->labelTotalValue->setText(
-            BitcoinUnits::formatWithUnit(unit, totalAmount, false, BitcoinUnits::SeparatorStyle::ALWAYS));
-        m_fee_formatted = BitcoinUnits::formatWithUnit(unit, GOVERNANCE_PROPOSAL_FEE_TX, false,
+            BitcoinUnits::formatWithUnit(unit, total, /*plussign=*/false, BitcoinUnits::SeparatorStyle::ALWAYS));
+        m_fee_formatted = BitcoinUnits::formatWithUnit(unit, GOVERNANCE_PROPOSAL_FEE_TX, /*plussign=*/false,
                                                        BitcoinUnits::SeparatorStyle::ALWAYS);
         m_ui->labelFeeValue->setText(m_fee_formatted.isEmpty() ? QString("-") : m_fee_formatted);
         // Dynamic header/subheader and prepare text
```
