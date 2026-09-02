### Title
Webhook `shop`, `topic`, `api_version` and `webhook_id` metadata are not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `HmacValidator.validate` proves nothing about the `shop-domain`, `topic`, `webhook-id`, or `api-version` HTTP headers. Since the same app `client_secret` is shared across every shop that installs the app, any merchant who legitimately receives a valid signed webhook for their own store can resend that exact body/HMAC pair to the app's webhook endpoint while substituting a different shop's domain (or a different topic) in the headers, and it will pass verification.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are never part of the signed payload: [2](#0-1) 

`Registry.process` trusts these unauthenticated header-derived fields once the body HMAC check passes: [3](#0-2) 

The identity binding that should hold is: `shop header == shop that the HMAC-signed body was generated for`. Because the HMAC only signs body bytes, this equality is never enforced — the "bytes verified" (raw body) are decoupled from "bytes/fields acted on" (shop, topic, webhook_id, api_version headers). A merchant possessing one valid signed webhook (received legitimately from Shopify for their own shop, using the shared `client_secret`) can replay the identical body+HMAC with a forged `x-shopify-shop-domain` (or `x-shopify-topic`) header. `HmacValidator.validate` still returns `true` because it only recomputes the HMAC over `@raw_body`, and `Registry.process` then dispatches the handler with the attacker-chosen `shop`/`topic`, since they're passed straight into `WebhookMetadata`.

### Impact Explanation
This breaks the tenant boundary the app relies on webhooks for: a host application that keys off `WebhookMetadata#shop` (e.g., to look up the shop's session/access token, or to run shop-scoped data operations like GDPR `customers/redact` or `app/uninstalled` cleanup) can be tricked into applying another shop's legitimate webhook payload as if it belonged to a victim shop, or into invoking a handler for a spoofed topic with attacker-controlled (but validly-signed) body content. This is a cross-tenant confused-deputy condition stemming purely from the gem's own verification logic.

### Likelihood Explanation
Any merchant that installs the app can legitimately receive valid signed webhooks from Shopify for their own store — no leaked secret or privileged access is required. The webhook endpoint is a public HTTP endpoint and headers are fully attacker-controlled in the replayed request, so the attack is straightforward for an unprivileged (but already-installed) merchant/attacker to execute.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable payload used for HMAC verification (or otherwise cryptographically bind them to the body), so header spoofing cannot pass the same signature intended for a different shop/topic/body combination.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`. Shopify sends a legitimate webhook, e.g. topic `customers/redact`, with headers:
   `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: customers/redact`, `x-shopify-hmac-sha256: <valid HMAC over raw body B>`.
2. Attacker resends the same raw body `B` and the same `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/webhooks/registry.rb:190` recomputes HMAC over `@raw_body` only (`lib/shopify_api/webhooks/request.rb:36-38`) — it matches, so validation succeeds.
4. `Registry.process` invokes the `customers/redact` handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198`), causing the host application to act on the victim shop using attacker-supplied, though validly-signed-for-a-different-shop, payload data.

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
