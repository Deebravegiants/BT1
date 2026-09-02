### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` value that is trusted and forwarded to the host application's webhook handler is read from an unauthenticated HTTP header. This breaks the intended binding `verified_bytes == acted_on_shop`, letting an attacker who controls any shop that has installed the app replay a validly-signed webhook body while forging the `shop-domain` header to impersonate a different (victim) shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, however, is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which plays no part in the signed payload: [2](#0-1) 

`HmacValidator.validate` verifies `verifiable_query.to_signable_string` (the body) against `verifiable_query.hmac`, so it never touches `shop`: [3](#0-2) 

`Registry.process` relies on that HMAC check as its sole authenticity gate, then unconditionally forwards `request.shop` into `WebhookMetadata`, which is handed to the host app's handler as the trusted shop identity: [4](#0-3) [5](#0-4) 

Because Shopify signs the webhook body using the app's single shared `api_secret_key` (the same key regardless of which shop the webhook originates from), the signature does not bind the payload to any particular shop. An attacker who has installed the app on a shop they control can capture one legitimately-signed `(raw_body, hmac)` pair from their own shop's webhook traffic, then POST that identical body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (it only checks the body), so `Registry.process` proceeds and calls the handler with `WebhookMetadata#shop` set to the forged victim domain.

The gem's own documentation reinforces the false assumption that HMAC validation authenticates the whole request including shop identity: "This will verify the request did indeed come from Shopify..." [6](#0-5) 

This is exactly the bug class described in the external report: an external function's output (`remainingMargin`'s `isInvalid`, here the header-derived `shop`) is used without validating that it is bound to the same trust anchor as the rest of the verified data (the HMAC-covered body).

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` to attribute incoming webhook data to a tenant (e.g., looking up a stored session/access token by shop, writing data keyed by shop, or triggering shop-specific side effects) can be tricked into processing an attacker-controlled payload under a victim shop's identity. Since the shop field is never bound to the HMAC, this is a cross-tenant identity confusion that lets an unprivileged attacker (who merely needs to install the app on their own store) inject arbitrary "verified" webhook payloads attributed to any other shop domain of their choosing.

### Likelihood Explanation
The attacker only needs: (1) their own shop where the app is installed (any unprivileged merchant/developer can do this), and (2) the ability to send an arbitrary HTTP POST with a forged header to the app's public webhook endpoint. Both are trivial and require no privileged credentials, matching the "unprivileged internet user" threat model.

### Recommendation
Bind the shop domain into the signed payload, or otherwise cryptographically verify it against the caller. In the near term, `Utils::HmacValidator`/`Registry.process` should not let host applications treat `request.shop` as verified — document this loudly, or better, have `Registry.process` reject requests where the shop cannot be corroborated (e.g., cross-checked against an active/known session for that shop) before invoking the handler.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, triggering a real Shopify webhook (e.g. `orders/create`) with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker replays a POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` as if Shopify itself sent this data on behalf of the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
