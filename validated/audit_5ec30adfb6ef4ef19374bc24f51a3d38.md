## Title
Webhook processing trusts the unauthenticated `shop` header as the tenant identity, allowing cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-validating the raw request body against the app's shared `api_secret_key`. The `shop` identity that is handed to the app's handler is read directly from the unauthenticated `X-Shopify-Shop-Domain` header and is never covered by that HMAC. Because the `api_secret_key` is the same for every shop that installs the app, any merchant who can obtain one legitimately-signed `(body, hmac)` pair from their own store can replay it to the app's public webhook endpoint while swapping the shop header to name a different, victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read straight from the `shop-domain` header without any cryptographic binding [2](#0-1) .

`Registry.process` validates the HMAC over that signable string (i.e., the body only) and, if it matches, immediately builds `WebhookMetadata` using `request.shop` — the unauthenticated header value — and forwards it to the registered handler: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the supplied signature: [4](#0-3) 

The identity binding that should hold is: `shop that Shopify actually sent this webhook for == shop passed to the handler`. Because `shop` is excluded from the signed bytes, and the secret is shared across every shop of the app, this equality is never enforced — the gem only proves "some shop of this app produced (or replayed) this body", not "this specific shop produced it".

### Impact Explanation
An attacker who legitimately installs the app on their own store (unprivileged merchant, no special access needed) can:
1. Trigger any webhook event on their own store to obtain a body they control along with a valid `X-Shopify-Hmac-Sha256` signature (computed with the app's `api_secret_key`, shared across all installs).
2. Send that exact `(body, hmac)` pair directly to the app's public webhook endpoint, but with `X-Shopify-Shop-Domain` changed to a victim shop's domain.
3. `Registry.process` passes the HMAC check (body+secret match) and calls the handler with `shop: "victim-shop.myshopify.com"`, while `body` contents are entirely attacker-controlled.

Any app logic that uses `WebhookMetadata#shop` to look up or mutate per-tenant state (e.g., store settings, order records, GDPR data-request/redact handling, cache keys) will act on the victim's tenant using attacker-supplied data — a cross-tenant data integrity/confidentiality violation achieved without any credential belonging to the victim.

### Likelihood Explanation
Any Shopify app using this gem's webhook pipeline is affected. The only prerequisite is that the attacker's own store can install the app (normal merchant self-service) and knows the endpoint URL, which is required to be public for Shopify's own delivery. No leaked secrets, tokens, or privileged access are required, and the endpoint is designed to accept unauthenticated inbound POSTs from the internet.

### Recommendation
Bind the `shop` field into the value that is authenticated before it is trusted:
- Verify that the `shop` header value corresponds to a shop actually registered/known to this app instance (e.g., cross-check against stored sessions/installations) before invoking the handler, and/or
- Where possible, include the shop domain in the material verified against Shopify (e.g. reject/flag webhooks whose declared shop has no active session/installation), so a replayed payload from a different tenant cannot be attributed to an arbitrary shop.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com"
# and captures a legitimately signed webhook, e.g. for orders/create:
body = '{"id":1,"note":"malicious payload"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, body)

# Attacker replays it directly to the app's public webhook endpoint,
# only changing the shop-domain header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HMAC validates (body/secret match); handler receives shop: "victim-shop.myshopify.com"
# with attacker-controlled body content.
``` [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
