## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

## Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` (tenant) identity is read from an unsigned header. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then hands the unauthenticated `shop` value straight to the app's handler, so a request whose body was legitimately signed for one shop can be replayed with a different `shop-domain` header to make the host app believe the payload came from another (victim) tenant.

## Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content at all: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string` (i.e. the raw body) using the app's single, shop-independent `api_secret_key`: [3](#0-2) 

`Registry.process` validates that HMAC and then immediately forwards the (unauthenticated) `request.shop` to the app's webhook handler as the tenant identity: [4](#0-3) 

The identity binding that should hold is: `shop-header == shop-that-the-HMAC-secret-actually-authenticates-the-body-for`. Because the HMAC only covers the body and the app uses one shared `api_secret_key` for every installed shop, this equality is never checked. Any two requests with the same body and the same app-wide secret produce the same valid HMAC regardless of which shop header accompanies them.

Concretely: an attacker installs the public app on their own (free/dev) store — an unprivileged action requiring no credentials belonging to the target. They create resources on their own store to control the webhook body content, and receive the resulting genuinely Shopify-signed webhook (`raw_body`, `x-shopify-hmac-sha256`) for their own shop. They then replay that exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint, but substitute the `x-shopify-shop-domain` header with the victim shop's domain. `HmacValidator.validate` still returns `true` because it only checks the body against the shared secret, and `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with `shop` now pointing at the victim.

## Impact Explanation
This breaks the tenant boundary the webhook subsystem is supposed to enforce: a request never sent by Shopify for the victim's shop is delivered to the app's handler tagged with the victim's shop identity. Any host application that (as encouraged by the gem's own docs, see `docs/usage/webhooks.md`) uses `data.shop` to select which merchant's records to create/update/delete will process attacker-controlled data under the victim's tenant — a cross-tenant data-integrity/confidentiality issue reachable purely through this gem's `Registry.process`/`Request` verification logic, without needing the victim's or the app's secrets.

## Likelihood Explanation
Likelihood is high for any real deployment: no privileged credentials, no MITM, and no access to the app's `client_secret` are needed. The attacker only needs to be able to install the target app on a shop they control (freely available to any developer) and can then craft/capture an arbitrarily-contented but validly-signed webhook body at will, then resend it to the target's public webhook endpoint with a forged shop header.

## Recommendation
Bind the `shop` field into the signed material, or otherwise cryptographically tie the header to the body, before trusting it:
- Include the `shop-domain` header value (and ideally `topic`/`webhook-id`) in the HMAC input (`to_signable_string`) so `HmacValidator.validate` fails if the shop header is altered independently of the body, or
- Look up the shop-scoped session/webhook registration by `webhook_id`/topic and cross-check it matches the claimed `shop` header before dispatching to the handler, rather than trusting the header as-is.

## Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (no special privileges required).
2. Attacker triggers/receives a genuine webhook: Shopify computes `hmac = HMAC-SHA256(api_secret_key, raw_body)` and POSTs headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <hmac>`, body `raw_body`.
3. Attacker resends the identical `raw_body`/`x-shopify-hmac-sha256` to the app's webhook endpoint, replacing only `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only re-hashes `raw_body` — see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:26-31`.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: attacker_controlled_body, ...)` — see `lib/shopify_api/webhooks/registry.rb:188-199` — making the app believe attacker-controlled content originated from the victim shop.

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
