The core issue is in the webhook processing path, where the HMAC signature and the tenant-identifying `shop` value are decoupled.

## Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) 
while the `shop` identity used downstream is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, with no cryptographic binding to that header at all [2](#0-1) .

### Finding Description
`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [3](#0-2) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against a signature computed from `verifiable_query.to_signable_string` [4](#0-3) . For the webhook `Request` class, `to_signable_string` is just the raw JSON body — it never includes the `shop`, `topic`, `webhook-id`, or `api-version` header values [1](#0-0) .

The app-level `api_secret_key` used for this HMAC is shared across **every** shop that has the app installed — it is not shop-specific. Any unprivileged actor can install the app on a shop they control (a free/dev store) and receive genuinely-signed webhook deliveries (valid `hmac-sha256` header for a given raw body) for that shop. Because the `shop-domain` header is completely outside the signed content, that same attacker can replay the identical `raw_body` + `hmac-sha256` pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g. a victim tenant's domain). `HmacValidator.validate` will still pass (the body/HMAC pair is valid), and `Registry.process` will invoke the handler with `shop: request.shop` set to the attacker-chosen value alongside attacker-influenced body content — the identity binding `verified-bytes == acted-upon-shop` is broken.

### Impact Explanation
This breaks the tenant boundary the host application relies on: `WebhookMetadata.shop` is the value apps use to route/store webhook data to the correct merchant record. An attacker who legitimately installs the app on one shop can spoof webhook deliveries "from" any other shop known to use the app, causing cross-tenant data corruption/injection in the host application's webhook handler — a cross-tenant access impact.

### Likelihood Explanation
Any internet user can install a public app on a store they control and thereby obtain a validly-HMAC-signed body/signature pair, then replay it directly to the app's public webhook endpoint with a forged shop-domain header — no privileged credentials, tokens, or social engineering required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the value that is HMAC-verified, or otherwise cross-check `request.shop` against a shop the app has an active/known session for before dispatching to the handler, so the header cannot be forged independently of the signed payload.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed with the app's shared `api_secret_key`).
2. Send a new HTTP POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` passes because it only checks `B`/`H` [5](#0-4) , and `Registry.process` calls the handler with `shop: "victim-shop.myshopify.com"`, processing attacker-supplied content under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
