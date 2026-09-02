### Title
Webhook shop-domain identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw HTTP body, while the `shop` (and `topic`, `webhook-id`, `api-version`) values used to dispatch and label the webhook are taken directly from unauthenticated HTTP headers that are never included in the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string`, i.e. only the raw body bytes: [2](#0-1) 

`Registry.process` then trusts `request.shop` (parsed from the `x-shopify-shop-domain`/`shopify-shop-domain` header, not from the signed body) to build the `WebhookMetadata` handed to the app's handler, after only checking the HMAC: [3](#0-2) [4](#0-3) 

This is the same bug class as the report: a field that is *acted on* (here, the `shop` identity attributed to the webhook payload) is not *covered by* the integrity check (the HMAC). Because a single app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, any merchant who has installed the app can obtain a validly-HMAC-signed webhook body for their own shop (e.g. by triggering an `orders/create` webhook on their own store), then replay that exact raw body while substituting the `x-shopify-shop-domain` header for a different (victim) shop's domain. `HmacValidator.validate` recomputes the HMAC over the unchanged raw body and it still matches, so the request is accepted as authentic; `Registry.process` then invokes the app's handler with `WebhookMetadata` claiming the body originated from the victim shop.

### Impact Explanation
This breaks the identity binding `shop-that-produced-and-signed-the-body == shop-attributed-to-the-processed-webhook`. Any app whose webhook handler uses `WebhookMetadata#shop` to key its data store, authorize actions, or select per-shop credentials/state can have attacker-controlled body content associated with an arbitrary victim shop id, corrupting that tenant's data or triggering shop-scoped side effects (cross-tenant data poisoning) — this satisfies the Critical "cross-tenant access" impact bar since it lets one tenant's request be attributed to and affect another tenant's records purely by header substitution.

### Likelihood Explanation
Likelihood is high for any unprivileged internet user who is (or can become) a merchant installing the vulnerable app on their own shop: they only need network access to send an HTTP request to the app's webhook endpoint with a copied valid raw body/HMAC pair and a forged `shop-domain` header — no access token, `api_secret_key`, or privileged account is required.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically/authoritatively verify that the `shop-domain` header matches the shop that produced the signed body (e.g., include the shop domain in the HMAC input, or cross-check `request.shop` against an allow-list of shops that are actually installed/active for the app before dispatching to a handler) in `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook topic (e.g. `orders/create`), capturing the exact `raw_body` and the corresponding `x-shopify-hmac-sha256` value Shopify sends.
2. Attacker sends the app's webhook endpoint the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the HMAC only covers `raw_body`. [5](#0-4) 
4. The app's handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, processing attacker-supplied body content under the victim's shop identity.

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
