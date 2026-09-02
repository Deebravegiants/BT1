### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `Request#shop` is read directly from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header. `Registry.process` validates the HMAC over the body only, then forwards the attacker-controllable `shop` header value straight into the handler's `WebhookMetadata`, so the tenant identity is never bound to the cryptographic signature.

### Finding Description
`HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to be only `@raw_body`: [2](#0-1) 

Meanwhile `shop` is parsed straight out of a header that carries no cryptographic protection at all: [3](#0-2) 

`Registry.process` validates the HMAC (over body only) and then dispatches to the app's handler using `request.shop` as the tenant identity, with no separate verification that the header matches any signed value: [4](#0-3) 

Because the app's `api_secret_key` is fixed per-app (not per-shop), any shop that installs the app receives genuinely Shopify-signed webhooks whose HMAC is valid for that exact body under the app's shared secret. Since the `shop` header is excluded from the signed payload, an attacker who controls their own installation can capture a legitimate `(body, hmac)` pair from a webhook Shopify sent for their own shop, then replay the identical body+HMAC to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. The HMAC check still passes (body unchanged, secret unchanged), so `Registry.process` accepts the request and calls the handler with `shop:` set to the attacker-chosen victim domain — breaking the intended binding of "shop verified by HMAC" == "shop attributed to the webhook data."

### Impact Explanation
This breaks the tenant-authentication boundary the gem is expected to provide to host applications: the `shop` value handed to webhook handlers is supposed to be the Shopify-authenticated origin of the event, but it is fully attacker-controlled once a valid body/HMAC pair from any shop (including the attacker's own) is obtained. A host application that trusts `WebhookMetadata#shop` to look up/act on a specific merchant's records (a common and encouraged pattern) can be made to apply another shop's webhook payload against a victim shop's tenant context — cross-tenant data confusion/corruption, including for security-sensitive mandatory topics like `customers/redact`, `customers/data_request`, and `shop/redact`.

### Likelihood Explanation
No privileged credentials, access tokens, or the app's `api_secret_key` are required — the attacker only needs to be an ordinary merchant who can install the target app on their own (e.g., free development) store to legitimately receive genuine Shopify-signed webhook bodies for known/predictable payloads, then replay them with a modified shop header against the app's public webhook endpoint.

### Recommendation
Include the shop domain (and other identity-bearing headers currently excluded, such as `webhook-id`) in the value that is HMAC-verified, or otherwise cryptographically bind the `shop` claim to the signed payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that `request.shop` is unauthenticated and must not be trusted for tenant attribution without an independent lookup (e.g., cross-checking against a known/registered shop for that webhook subscription).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. topic `customers/redact` with some JSON body `B`, signed as `HMAC = HMAC-SHA256(api_secret_key, B)` in header `X-Shopify-Hmac-Sha256`, and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends the exact same body `B` and the exact same `X-Shopify-Hmac-Sha256` value to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` (unchanged) and it matches — validation succeeds: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)`, even though Shopify never sent this event for `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
