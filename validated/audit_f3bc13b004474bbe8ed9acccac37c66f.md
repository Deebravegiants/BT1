### Title
Webhook HMAC does not bind to the `shop` (or `topic`/`webhook-id`) header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, and `Registry.process` validates that body against the `hmac-sha256` header. The `shop-domain` header — which is the value handed to the host application as the tenant identity for the webhook — is never part of the signed material. Any attacker who can obtain one validly-signed webhook (trivially done by installing the app on their own store and triggering a webhook) can replay that exact body+HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` header, and the HMAC check still passes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC solely over that signable string: [2](#0-1) 

`Registry.process` uses this validation as the sole authenticity check, then immediately trusts `request.shop` (parsed straight from the `shop-domain` header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`request.shop` is read directly from the header with no cross-check against the HMAC-covered content: [4](#0-3) 

Because a single `api_secret_key` is shared by the app across all installed shops, `HMAC(secret, body)` is identical no matter which shop actually generated that body. This breaks the intended identity binding: `shop authenticated (by virtue of a validly-HMAC'd request) == shop the data is attributed to (header value)`. The header is fully attacker-controlled and unauthenticated, while the HMAC only proves "some install of this app produced this body," not "this specific shop produced this body."

### Impact Explanation
An unprivileged internet user can install the target app on a shop they control (or use a dev/trial store), trigger any webhook topic they like to receive a validly-signed `(body, hmac)` pair, then POST that same pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header set to a victim merchant's domain. `Registry.process` will accept it as authentic and dispatch `WebhookMetadata` with the attacker-chosen `shop` value to the host application's handler. Any host app that uses `data.shop` to look up records, update tenant state, or gate mandatory-compliance actions (e.g., `customers/redact`, `shop/redact`) can be manipulated into applying attacker-crafted data to a different tenant — a cross-tenant data integrity/confidentiality issue.

### Likelihood Explanation
Obtaining a legitimately-signed webhook body requires only installing the app on any store (including the attacker's own free/dev store) — no privileged account, leaked secret, or social engineering is needed. Replaying it with a modified header is a simple unauthenticated HTTP request to the app's public webhook endpoint.

### Recommendation
Bind the shop identity to the signed material: include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-signed content, or independently verify the shop-domain header against the known/expected shop for that install before trusting it (e.g., cross-check with a per-shop token/secret, or validate the shop against the app's installed-shops registry) rather than passing the raw header value straight into `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw request body `B` and the `X-Shopify-Hmac-Sha256` header `H` sent by Shopify (valid because `H = HMAC(api_secret_key, B)`).
2. Attacker sends a forged POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B) == H`, per `lib/shopify_api/utils/hmac_validator.rb` and `lib/shopify_api/webhooks/request.rb`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) dispatches the handler with `shop: "victim-shop.myshopify.com"`, and the host application processes attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
