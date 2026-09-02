### Title
Webhook shop/topic identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body, then trusts the `shop`, `topic`, and `webhook_id` values taken from HTTP headers that are never included in that signature. This breaks the intended identity binding `HMAC-verified bytes == bytes the app acts on`, because the value the app treats as "this webhook belongs to shop X" is not part of what was actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated headers: [2](#0-1) 

`Registry.process` verifies the HMAC (which only covers `@raw_body`) and then forwards `request.shop` and `request.topic` — values that were never part of the signed data — straight to the app's handler: [3](#0-2) 

`HmacValidator.validate` / `compute_signature` confirms that only `verifiable_query.to_signable_string` (the body, for webhooks) is HMAC-checked — nothing else: [4](#0-3) 

This is exactly the bug class described in the report: a field the application acts on (`shop`) is not covered by the integrity check (`HMAC`) that is supposed to bind the whole request to a specific tenant. The binding that should hold is:

`HMAC_valid(body, shared_secret) == true` should imply `shop header == the shop that legitimately produced (body, HMAC)`

but because the HMAC only signs `body`, the equality is actually:

`HMAC_valid(body) == true` (says nothing about `shop`/`topic`/`webhook_id`)

Since Shopify webhooks for a given app are all signed with the same `api_secret_key` regardless of which shop triggered them, any shop that has installed the app (an unprivileged action — installing/using your own free/dev Shopify store) receives webhooks whose body+HMAC pair is valid for the app's shared secret. Documentation explicitly instructs apps to pass `data.shop` from the webhook straight into business logic such as job dispatch keyed by shop: [5](#0-4) 

An attacker who controls Shop B can capture one of their own legitimately HMAC-signed webhook bodies and replay it to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) header to any target shop domain. `Registry.process` will accept it (HMAC validates because the body is unchanged) and hand the forged `shop` value to the handler as if it originated from the victim tenant.

### Impact Explanation
This is a cross-tenant identity confusion: the gem allows an unprivileged Shopify merchant/tenant (attacker) to make the host application process a webhook body under the identity of any other tenant, because the field carrying tenant identity (`shop`) is excluded from the cryptographic binding that is otherwise assumed to prove authenticity. Any host application logic keyed on `data.shop` (job dispatch, record lookups/updates, session resolution) can be poisoned with attacker-chosen body content attributed to a victim shop, which the rules classify as cross-tenant access — a Critical-tier impact.

### Likelihood Explanation
Requires only: (1) the attacker owns/operates a Shopify store that has the target app installed (or otherwise receives real webhooks signed with the app's `api_secret_key` — a value shared across all installs of the same app, not secret to any one tenant), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is inherent to any public webhook receiver. No access to `api_secret_key`, access tokens, or privileged accounts is needed by the attacker; they only need their own webhook traffic that Shopify legitimately signs for them.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, and ideally `webhook_id`) in the HMAC-signed material, or independently authenticate `shop` against a trusted, per-tenant session/installation record before invoking the handler, rather than trusting it purely because "some webhook body from this app" was HMAC-valid. At minimum, `Registry.process` should reject the request if the `shop` header does not correspond to a shop with an active installation/session, closing the gap between "HMAC covers only the body" and "app-facing metadata that determines tenant scope."

### Proof of Concept
1. Attacker installs the target app on their own Shopify dev store (`attacker-shop.myshopify.com`) — unprivileged, self-service action.
2. Shopify sends a legitimate webhook to the app for `attacker-shop.myshopify.com` with body `B` and header `X-Shopify-Hmac-Sha256: HMAC(B, api_secret_key)`.
3. Attacker captures this request (own traffic) and replays it directly to the app's public webhook endpoint, keeping `raw_body = B` and the original valid `X-Shopify-Hmac-Sha256` header, but changing `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`).
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(request.to_signable_string, api_secret_key)` — i.e., `HMAC(B, api_secret_key)` — and it matches, since `B` is unchanged. [6](#0-5) 
5. The handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B`, even though `victim-shop` never sent or authorized this webhook. [7](#0-6)

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

**File:** docs/usage/webhooks.md (L19-30)
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
```
