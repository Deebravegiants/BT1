### Title
Webhook shop domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by checking only that the raw body's HMAC matches, but it then trusts the `shop` value taken from an unsigned HTTP header when building the `WebhookMetadata` passed to the app's handler. Because the app's webhook secret (`api_secret_key`) is shared across every shop that installs the app, any shop-owning attacker who receives a legitimately signed webhook for their own shop can replay it against the app's webhook endpoint with the `shop-domain` header swapped to a victim shop, and the request will still pass HMAC validation.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body: [1](#0-0) [2](#0-1) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) and are not part of the signed string: [3](#0-2) 

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string`, i.e. only the body, and compares it with the `hmac-sha256` header: [4](#0-3) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` (the unsigned header) into `WebhookMetadata`, which is delivered to the app's handler as the shop identity of the event: [5](#0-4) 

The documented usage pattern shows host apps trusting `data.shop` directly to scope background work (e.g. `perform_later(shop_domain: data.shop, webhook: data.body)`): [6](#0-5) 

Since Shopify computes the webhook HMAC using the app's single, shared `api_secret_key` (not a per-shop secret), any merchant who installs the app can receive a validly-signed webhook for events on their own shop. Because the shop-domain header sits outside the HMAC-covered bytes, that same attacker can resend the identical `(body, hmac)` pair to the app's webhook endpoint while substituting a different `shop-domain` header value naming a victim shop. `HmacValidator.validate` will still return `true` because it only checks body bytes against the secret, and `Registry.process` will hand the forged shop identity to the handler as if it were an authentic event from the victim shop.

This breaks the identity binding: `shop_header_verified_by_hmac == shop_header_delivered_to_handler` does not hold — the HMAC verifies the body was signed by Shopify for *some* shop, but the `shop` value used downstream is never authenticated.

### Impact Explanation
This is a cross-tenant identity spoofing vulnerability. An attacker who is a legitimate (unprivileged) merchant with the app installed on their own store can forge webhook events that host applications attribute to an arbitrary victim shop domain, with attacker-controlled body content within the shape of a valid topic payload. Depending on how the host app scopes side effects by `shop` (order sync, GDPR redaction handling, app/uninstalled cleanup, etc., as shown in the gem's own documented handler pattern), this can lead to cross-tenant data corruption, spoofed compliance/redaction events, or state confusion for a shop the attacker does not own or have access to — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
No stolen credentials, access tokens, or `client_secret` are required — only a normal app installation by the attacker (a genuinely unprivileged internet user) to obtain one validly-signed webhook body/HMAC pair, plus the ability to send an arbitrary HTTP request with a modified header to the app's public webhook endpoint. The gem provides no mechanism, and the documented handler pattern encourages none, to verify that the `shop` header is bound to the HMAC-signed body.

### Recommendation
Extend `to_signable_string`/HMAC verification (or add a secondary check) so that the shop domain (and ideally topic/webhook id) are cryptographically bound to the verified payload, or require host applications to cross-check `data.shop` against an independently known/registered shop before trusting it (e.g., verify the webhook's `shop` matches a shop with an active, previously-established session/registration for that specific webhook subscription) rather than trusting the header value implicitly once body HMAC passes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and registers for a webhook topic (e.g. `customers/data_request`).
2. Shopify sends a legitimately signed webhook to the app's endpoint: body `B`, header `X-Shopify-Hmac-Sha256: H` (computed with the app's single `api_secret_key`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker replays the exact same `raw_body` and `X-Shopify-Hmac-Sha256` header to the same endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `HmacValidator.validate` recomputes the HMAC solely from `@raw_body` per [1](#0-0)  and it matches `H`, so validation succeeds.
5. `Registry.process` calls the app handler with `WebhookMetadata` where `shop == "victim.myshopify.com"`, per [7](#0-6) , even though the request never originated for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
