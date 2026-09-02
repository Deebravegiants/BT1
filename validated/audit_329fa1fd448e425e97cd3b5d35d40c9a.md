### Title
Webhook HMAC Does Not Bind the `shop`/`topic`/`webhook-id` Headers, Enabling Cross-Tenant Webhook Replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop`, `topic`, `webhook-id`, and `api-version` values that are handed to the app's webhook handler come from unauthenticated HTTP headers that are never included in the HMAC-signed content. This breaks the intended binding `hmac_signed_bytes == identity_bytes_used_by_handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

All the identity fields the app actually acts on — `shop`, `topic`, `webhook_id`, `api_version` — are read straight from HTTP headers that are not part of that signable string: [2](#0-1) 

`Registry.process` only checks the HMAC of the body before dispatching to the handler with these unauthenticated header values: [3](#0-2) 

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`, i.e. the raw body for webhook requests, with no reference to `shop`/`topic`/`webhook_id`: [4](#0-3) 

Because the signature covers only the body, any `(raw_body, hmac)` pair that was legitimately produced by Shopify for one shop/topic remains a valid `(raw_body, hmac)` pair for *any* other shop or topic. An attacker who can obtain a single legitimate webhook delivery for a body they can influence (trivial: install the target app on a free Shopify development store they control, and trigger a webhook whose payload is attacker-influenced, e.g. `products/create` where the JSON body contains attacker-chosen field values) can then replay that exact `raw_body` + `hmac` to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for an arbitrary target shop. `HmacValidator.validate` still passes because it never looks at the headers, and `Registry.process` calls the registered handler with `shop: <attacker-chosen shop>` and the attacker-controlled body, i.e. `WebhookMetadata.new(shop: request.shop, body: request.parsed_body, ...)`.

This is precisely the "field acted on but not covered by the HMAC" identity-binding break: the equality that should hold, `hmac == HMAC(secret, body ++ shop ++ topic)`, is instead only `hmac == HMAC(secret, body)`, letting an attacker vary `shop`/`topic` freely post-verification.

### Impact Explanation
Any app built on this gem that stores or acts on webhook data keyed by `data.shop` (the documented, expected usage pattern — see `WebhookMetadata`) can be made to attribute attacker-supplied data to a victim merchant's tenant. This is a cross-tenant data-integrity/access issue: attacker-controlled data (e.g., fake order/product/customer records, GDPR-topic payloads, `app/uninstalled` signals) can be injected into a different shop's stored state, without any credentials belonging to that shop. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only an unprivileged actor who can install the target app on any Shopify store (including a free development store) to obtain one genuine `(raw_body, hmac)` sample, then replay it with a modified `Shop-Domain`/`Topic` header to the app's public webhook endpoint. No access token, `client_secret`, or `api_secret_key` is required — the attacker never needs to compute an HMAC themselves, only to reuse a validly-signed one. This is fully reachable via this gem's own `Registry.process`/`HmacValidator.validate` code path.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`) in the HMAC-signable content used by `Webhooks::Request`, or otherwise cryptographically bind the header values to the signature (e.g., by having `HmacValidator` validate a canonical string that concatenates body + shop + topic, consistent with how `Oauth::AuthQuery#to_signable_string` already includes `shop` in its signed content). At minimum, document and enforce that `shop`/`topic` must not be trusted as tenant identifiers unless bound into the signature.

### Proof of Concept
1. Attacker creates/uses a Shopify development store and installs the target app, registering a webhook (e.g. `products/create`) whose JSON body includes attacker-chosen content.
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `X-Shopify-Hmac-Sha256: H`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: products/create`, and body `B`. Attacker captures `(B, H)`.
3. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `H` against `HMAC(secret, B)`: [5](#0-4) 
5. The registered handler is invoked with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, even though `victim-shop` never sent this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
