### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` header values — which are handed to the app's handler as the trusted tenant/event identity — are never included in the signed data. Because all shops that install the same app share one `client_secret`, any user of the app who can generate a legitimately-signed webhook for their own shop can trivially forge a webhook impersonating another tenant by re-sending the same body/HMAC pair with a different `shop-domain` header.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string (i.e., the body) and compares it with `OpenSSL.secure_compare`: [2](#0-1) 

`Registry.process` uses this single check as the sole authentication gate, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which participated in the HMAC — and forwards them to the app-provided handler as the tenant/event identity: [3](#0-2) 

The `shop` field is read straight from an attacker-controllable HTTP header with no cryptographic binding to the signed content: [4](#0-3) 

The identity binding that should hold is:
`HMAC(client_secret, body) valid` **should imply** `shop == the shop that actually generated that (body, HMAC) pair`

but the code only proves `HMAC(client_secret, body) valid`, and separately trusts whatever `shop` header accompanies the request. Since `client_secret` is shared by the app across all installing shops (not shop-specific), any legitimate merchant using the app can trigger a webhook on their own store (e.g., `orders/create` with attacker-chosen order data), capture the resulting valid `(raw_body, hmac)` pair from Shopify, and replay it against the app's webhook endpoint with `x-shopify-shop-domain` set to a victim shop's domain. `Registry.process` will accept it as authentic, and the app's handler receives `WebhookMetadata` with `shop` set to the victim's domain while `body` is fully attacker-controlled. This is documented in `docs/usage/webhooks.md` as the correct/only integration pattern — the gem gives host apps no indication that `shop`, `topic`, or `webhook_id` require independent verification, and no API exists in this gem to do so.

This is directly analogous to the reported bug class: a value used to make a security/identity decision (here, tenant attribution) is not covered by the cryptographic check meant to guarantee its authenticity, exactly like an unbonding transaction being trusted without validating that the returned signature actually matches the transaction it is supposed to cover.

### Impact Explanation
This breaks the tenant isolation boundary that host applications rely on this gem to enforce. Since the shop identity is unauthenticated, an attacker who is a legitimate (even free-trial) merchant on the app can forge webhook events attributed to any other shop using the same app. Depending on how the host app's handler uses `data.shop` (e.g., updating billing state, inventory, order records, GDPR/mandatory topics, triggering emails, or writing to a per-shop database keyed by `data.shop`), this enables cross-tenant data corruption or cross-tenant action injection — qualifying as Critical (cross-tenant access) per the impact taxonomy.

### Likelihood Explanation
High. No secrets beyond ordinary app installation are required — only the ability to install/operate the vulnerable app on one's own store (any developer/merchant can do this for free in a dev store) to legitimately mint valid `(body, HMAC)` pairs, and then send a crafted HTTP POST with a spoofed `x-shopify-shop-domain` header to the app's public webhook endpoint. No rate limiting or additional Shopify-side check gates this at the library level.

### Recommendation
Bind the identity fields into the signed data used for HMAC verification, or otherwise cryptographically or out-of-band verify that the `shop`, `topic`, and `webhook_id` headers correspond to the shop that Shopify actually sent the webhook for (e.g., by validating the webhook against Shopify's webhook ID/shop pairing via an authenticated API call, or documenting/enforcing that the app must independently confirm the shop has app installation state matching the claimed `shop` header before trusting the payload). At minimum, the gem should not present `request.shop` as a value implicitly protected by `Registry.process`'s HMAC check; the HMAC only guarantees body integrity, not sender identity, and this distinction must be surfaced to consumers of the API or fixed by making `to_signable_string` incorporate the identity headers where such a scheme is supported by Shopify's webhook signing format.

### Proof of Concept
1. Attacker installs the app on their own throwaway store `attacker.myshopify.com` (any account can do this).
2. Attacker triggers `orders/create` (or any registered topic) with a crafted order payload.
3. Shopify sends a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw body>`, and the crafted JSON body.
4. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from this legitimate request (e.g., via a proxy they control, or by making the app log/echo it).
5. Attacker sends a new POST directly to the app's public webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
6. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks the body/HMAC: [5](#0-4) 
7. `Registry.process` invokes the app's handler with `WebhookMetadata` where `shop == "victim.myshopify.com"` but `body` is entirely attacker-authored: [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
