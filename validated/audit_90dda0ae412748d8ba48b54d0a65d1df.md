### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain` header from the HMAC-covered content. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC is correct, then unconditionally trusts `request.shop` (parsed straight from the unauthenticated header) to build the `WebhookMetadata` passed to the app's webhook handler. Because a single `api_secret_key` is shared across every shop that has installed the app, a valid `(body, hmac)` pair obtained from a webhook delivered to any shop (including one an attacker controls, e.g. their own free dev store) remains cryptographically valid when replayed with a different `shop-domain` header, letting an attacker impersonate another tenant.

### Finding Description
The identity binding that should hold is:
`hmac == HMAC(secret, bytes_verified)` **and** `bytes_verified` should include everything the receiver later treats as authenticated (topic, shop, body) — but in this gem `bytes_verified` covers **only the body**, while `shop` is a value the receiver treats as authenticated when dispatching to app code.

- `Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 
- `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the HMAC: [2](#0-1) 
- `HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, i.e. the body, and compares it with `OpenSSL.secure_compare`: [3](#0-2) 
- `Registry.process` performs the HMAC check and then immediately forwards the unauthenticated `request.shop` value to the handler as if it were verified: [4](#0-3) 

Because the same app `client_secret`/`api_secret_key` is used for every shop that installs the app, any `(body, hmac)` pair that is valid for one shop remains valid (same signature check) if replayed with a different `shop-domain` header value. An unprivileged internet user can obtain such a valid pair simply by installing the target app on their own store (or a free development store) and capturing a webhook delivery Shopify sends them — no leaked credentials, access tokens, or `api_secret_key` knowledge are required. They can then POST that same body and HMAC to the app's webhook endpoint while substituting the victim's shop domain in the header.

### Impact Explanation
Any app built on this gem that relies on `data.shop` from `WebhookMetadata` to select which merchant's data/session/access token to act on (a common, gem-encouraged pattern, since `WebhookMetadata` is the only shop identifier surfaced to the handler) can be tricked into performing an action attributed to, or affecting data belonging to, a different, unrelated tenant. This is a cross-tenant confusion vulnerability: the attacker fully controls the `shop` value used to route/attribute webhook processing while only needing a self-obtained valid signature. Depending on the handler's logic (e.g., updating cached records keyed by shop, revoking data, marking GDPR redaction, altering per-shop state) this can corrupt or leak another merchant's data — a cross-tenant access issue.

### Likelihood Explanation
Likelihood is high for any actor willing to install the target public app on their own (free) development store: they obtain a legitimately signed `(body, hmac)` pair with zero cost and no privileged access, then only need to swap one plaintext header value before replaying the POST to the app's public webhook endpoint. No secret material, token, or social engineering is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signed content that is verified, or independently verify that `request.shop` matches the shop associated with the currently active installation/session before trusting it in `Registry.process`. At minimum, document that host applications must not treat the webhook `shop` header as authenticated by the HMAC and must cross-check it against records established during OAuth (e.g., verify the shop has an existing session/access token before acting on the webhook), rather than trusting the header value directly as this gem currently allows.

### Proof of Concept
1. Install the target Shopify app (built with this gem) on an attacker-controlled development store `attacker-shop.myshopify.com`.
2. Trigger any webhook topic the app subscribes to (e.g., create a product) and capture the resulting POST request, including its raw body and the `x-shopify-hmac-sha256` header — this HMAC is valid because it was computed by Shopify using the app's real `api_secret_key`.
3. Replay the exact same POST (same body, same `x-shopify-hmac-sha256`) to the app's webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks the body's HMAC (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` dispatches to the handler with `shop: request.shop` set to `victim-shop.myshopify.com` (`lib/shopify_api/webhooks/registry.rb:198`), even though the payload was never generated for, nor authorized by, that shop.

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
