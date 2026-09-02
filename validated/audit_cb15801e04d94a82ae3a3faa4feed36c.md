### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC computed over the raw request body, then trusts the unauthenticated `shop-domain` header to identify which tenant the webhook belongs to. Because the `shop` (and `topic`/`webhook_id`) header values are never included in the signed material, any party who can obtain one valid `(raw_body, hmac)` pair — e.g. from their own shop's install of the app — can replay it to the app's public webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` header and have it accepted as a legitimate webhook for a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors simply read directly from unauthenticated HTTP headers, none of which participate in `to_signable_string`: [2](#0-1) 

`Registry.process` validates the request using only this HMAC-over-body check, then immediately forwards `request.shop` (and `request.topic`) to the registered handler as trusted tenant/topic identifiers: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header — since `to_signable_string` is only the body, the signature is completely independent of which shop the header claims to be from: [4](#0-3) 

The gem's own documentation instructs app developers to trust `data.shop` from the processed webhook as the tenant key to route work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), which is exactly the field that is not bound to the signature: [5](#0-4) 

This breaks the intended identity binding: `hmac(raw_body, api_secret_key) == valid` should imply `shop header == the shop that actually generated this body`, but the equality the code actually checks is only `hmac(raw_body, api_secret_key) == valid`, with `shop` left completely unconstrained.

### Impact Explanation
Since `api_secret_key` is shared across all shops that install a given app, any attacker who operates (or has installed the app on) their own Shopify store can trigger a legitimate webhook delivery to their own endpoint, capture the `(raw_body, X-Shopify-Hmac-Sha256)` pair, and then send an HTTP POST directly to the target app's public webhook URL with the same body/HMAC but an `X-Shopify-Shop-Domain` header (and optionally `X-Shopify-Topic`) set to a victim shop of their choosing. `Registry.process` will accept it as authentic and dispatch it to the handler labelled as the victim shop, letting the attacker inject arbitrary webhook payloads (subject to reusing a valid signed body shape) attributed to another tenant. Depending on how the host app uses `data.shop`/`data.body` (e.g., updating orders/products/inventory or triggering shop-specific business logic keyed off `data.shop`), this can result in cross-tenant data corruption or unauthorized actions performed against a victim's account — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires only: (1) an attacker-controlled or attacker-installed shop that can receive at least one legitimate webhook (trivial — a developer/test store is free and easy to obtain), and (2) knowledge of the target app's public webhook endpoint URL (typically discoverable/guessable, e.g. `/webhooks/<topic>`). No access token, `api_secret_key`, or privileged account for the *victim* shop is required. This is a low-effort, unprivileged-internet-facing attack path.

### Recommendation
Bind the tenant/topic identity to the signed payload rather than trusting bare headers:
- Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (or otherwise cryptographically bind them to the body), so a captured `(body, hmac)` pair from one shop cannot be replayed with a different shop header.
- Alternatively/additionally, validate that the `shop` header matches an actual shop known to have this webhook topic registered (cross-check against stored registrations) before dispatching to the handler.
- Document explicitly that `data.shop` is not currently covered by the HMAC and must not be trusted without additional verification, until the binding is fixed.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC_SHA256(api_secret_key, B)`. Attacker captures `B` and `H` (e.g., by controlling a proxy in front of their own dev store's webhook receiver, or by using ngrok/logging on their own endpoint).
3. Attacker crafts a new POST request directly to the target app's public webhook route with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs the body)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (attacker-controlled, not signed)
   - `X-Shopify-Topic: orders/create`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` is only `B`.
5. The registered handler is invoked with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "orders/create", body: parsed(B), ...)`, and the host application processes attacker-supplied content as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
