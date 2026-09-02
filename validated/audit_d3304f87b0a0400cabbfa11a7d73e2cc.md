### Title
Webhook `shop-domain` and `topic` fields are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies incoming webhooks by HMAC-ing only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers and forwarded to the app's handler as if they were verified. An attacker who can obtain any single valid `(raw_body, hmac)` pair (e.g. by owning/controlling a shop that has the app installed) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, causing the host application to process the event as if it came from a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw request body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight out of HTTP headers, which are not part of the signed material at all: [3](#0-2) 

`Registry.process` validates the HMAC over the body only, then trusts `request.shop` and `request.topic` (both header-derived, unsigned) to dispatch the event and build the metadata handed to the app's business logic: [4](#0-3) 

This is exactly the identity-binding break called out in the prompt's rules: "bytes verified versus bytes parsed." The gem verifies the *body* bytes with HMAC, but the *shop identity* used for all downstream tenant attribution (`WebhookMetadata#shop`) is parsed from headers that sit entirely outside the HMAC's coverage. Any header value can be substituted without invalidating the signature check, because the signature never covered it.

**Exploitation path:** an unprivileged attacker who operates their own shop (e.g. a free/dev store) can install the target app, trigger a real webhook (e.g. `orders/create`) to capture one legitimate `(raw_body, hmac)` pair signed with the app's `client_secret` for their own shop, then replay that exact body and HMAC to the app's webhook endpoint while changing only the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` calls the handler with `shop: <victim-shop>` and the attacker-crafted body content, even though the victim shop never sent this webhook.

### Impact Explanation
Because host applications commonly use the `shop` field of `WebhookMetadata` to select which merchant's data/session/access token to act on (e.g. `Session storage lookup by shop`, then perform writes, cancellations, uninstalls, or GDPR-style data deletions), an attacker can trick the app into performing shop-scoped side effects attributed to, or executed against, a victim shop's tenant data using an attacker-forged payload. This is a cross-tenant identity confusion: the shop that is cryptographically bound to the signed payload (none, since shop isn't signed) differs from the shop the app believes originated the event. Depending on how the host app wires webhook handling into tenant-scoped storage, this can lead to cross-tenant data corruption/action — matching the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Requires no credentials, tokens, or privileged access — only that the attacker can install the app on a shop they control (many apps offer free installs / dev stores) to obtain one valid `(raw_body, hmac)` sample, and can then send arbitrary HTTP requests with attacker-chosen headers to the app's public webhook endpoint. The gem itself performs no additional binding between the signed body and the shop/topic headers, so likelihood of successful replay is high wherever the host app relies on `WebhookMetadata#shop`/`#topic` for tenant or event routing.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before verification — e.g. compute/verify the HMAC over a canonical string that concatenates body plus these header values, similar to `Auth::Oauth::AuthQuery#to_signable_string` which binds `shop`, `state`, `host`, etc. into the signed payload. At minimum, document and enforce that consuming applications must independently verify `request.shop` against a shop they expect (e.g. cross-check against an existing session) rather than trusting it as authenticated solely because the overall webhook HMAC passed.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed and
# captures a legitimate webhook delivery (body + hmac) sent by Shopify.
captured_body = '{"id":123,"note":"legit order"}'
captured_hmac = OpenSSL::HMAC.digest(
  OpenSSL::Digest.new("sha256"),
  app_client_secret,          # unknown to attacker; captured signature reused as-is
  captured_body,
)

# Attacker replays the same body/hmac, but swaps the shop-domain header
forged_headers = {
  "x-shopify-topic"       => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(captured_hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # <-- not covered by HMAC
  "x-shopify-webhook-id"  => "forged-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)

# HMAC validation still passes because to_signable_string only returns @raw_body
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process dispatches to the handler believing this event is
# from "victim-shop.myshopify.com", even though it never sent it.
ShopifyAPI::Webhooks::Registry.process(request)
```
This demonstrates that `shop` (and `topic`/`webhook_id`/`api_version`) can be freely substituted without invalidating the webhook's HMAC, because [5](#0-4)  signs only the body, breaking the intended binding between the verified bytes and the shop identity acted upon by [6](#0-5) .

### Citations

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
