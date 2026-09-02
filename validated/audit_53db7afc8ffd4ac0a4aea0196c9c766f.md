The docs explicitly claim `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), and the returned `data.shop` field is documented as "The shop domain of the webhook" (docs/usage/webhooks.md:14) — implying it's part of the verified webhook data. But the HMAC only covers the raw body, not the `shop` header.

### Title
Webhook `shop` identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing via header substitution - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` in `Registry.process` only authenticates the request body — it never binds the `shop` (or `topic`/`webhook_id`) header values to the signature [2](#0-1) . Yet `Registry.process` passes `request.shop`, taken straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) , directly into `WebhookMetadata` given to the app's handler, with the documentation telling integrators this value is verified/trustworthy shop identity [4](#0-3) .

### Finding Description
The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_tenant_identity`. Here it breaks down: `HmacValidator.validate` verifies `OpenSSL::HMAC(secret, raw_body)` against the `hmac-sha256` header [5](#0-4) , but `shop`, `topic`, and `webhook_id` are read from separate, unsigned HTTP headers [6](#0-5) . Because the raw body for a given topic (e.g., a specific `orders/create` payload) is frequently identical or predictable across multiple merchant shops (for the same app), an attacker who has observed one legitimate webhook delivery for Shop A (its body + a valid HMAC computed over that body) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header to Shop B (or any arbitrary shop domain string). `HmacValidator.validate` will still pass, because it only checks the body against the signature — it has no dependency on the shop header at all [7](#0-6) . `Registry.process` then dispatches to the handler with the attacker-controlled `shop` value [2](#0-1) .

### Impact Explanation
This is a cross-tenant identity confusion: the app's webhook handler believes the event body belongs to shop B (per the documented, "verified" `data.shop`) when it actually was HMAC-authenticated only for the body originally generated for shop A. Any app logic that trusts `data.shop` to select the merchant record/session to update (e.g., writing order data, updating settings, or associating billing/webhook state) can be tricked into applying shop-A's data under shop-B's tenant, or vice versa — a cross-tenant data integrity break rooted in the gem's own verification routine, which the gem's docs claim fully verifies "the request did indeed come from Shopify."

### Likelihood Explanation
Exploitation requires the attacker to have observed at least one legitimate webhook delivery's raw body + HMAC pair (e.g., via a compromised/malicious shop the attacker controls that triggers the same webhook topic with attacker-influenced content, or via traffic capture), then replay the same body to the app's public webhook endpoint with a forged `shop` header — no `api_secret_key`, access token, or privileged access is needed, only the ability to send a raw HTTP POST with attacker-controlled headers.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) values into the signed material, or require the caller to independently verify the `shop` header against an out-of-band trusted registry/session store before trusting `WebhookMetadata#shop`. At minimum, update `VerifiableQuery#to_signable_string` for webhooks to incorporate the shop-domain header the same way Shopify's real signing scheme intends, so `HmacValidator.validate` cannot be satisfied by a replayed body under a substituted shop identity.

### Proof of Concept
1. Attacker triggers (or otherwise obtains) a legitimate webhook delivery for `shop-a.myshopify.com` with topic `orders/create`: raw body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(secret, B)`.
2. Attacker sends a POST to the app's webhook endpoint with the same raw body `B`, the same `x-shopify-hmac-sha256: H` header, but `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "shop-b.myshopify.com", hmac-sha256: H})` is constructed; `to_signable_string` returns `B` only [1](#0-0) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(secret, B)` and compares to `H` — this matches, so validation passes [8](#0-7) .
5. The handler is invoked with `WebhookMetadata.new(topic:, shop: "shop-b.myshopify.com", body: parsed_body(B), ...)` [9](#0-8)  — shop-A's authenticated body is now processed under shop-B's identity.

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

**File:** docs/usage/webhooks.md (L123-135)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
