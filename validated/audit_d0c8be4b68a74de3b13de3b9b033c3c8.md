### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`, `api_version`, `webhook_id`) attributes are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body only and then forwards `request.shop` straight into `WebhookMetadata`, which the host application's handler uses to attribute the webhook to a tenant. The identity binding the gem implicitly promises — "the `shop` an app handler acts on == the shop Shopify's HMAC actually vouches for" — does not hold, because the HMAC never covers the `shop` field.

### Finding Description
`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, and for webhooks that string is just `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values used elsewhere are pulled straight from HTTP headers, none of which are part of the signed material: [2](#0-1) 

`Registry.process` validates only the HMAC and then immediately trusts `request.shop` to build `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the event: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` const with no further verification: [4](#0-3) 

Because the app's HMAC secret (`api_secret_key`) is shared across *all* shops that install the app (it is not a per-shop key), any merchant who legitimately installs the app receives real webhook deliveries — `raw_body` + a valid `x-shopify-hmac-sha256` — for their own shop. That attacker-controlled shop can capture one such legitimate `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. Since `shop-domain` is never part of `to_signable_string`, the HMAC still validates, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from the victim shop, while the payload was actually authored by the attacker.

The equality that should hold but doesn't:
`shop attributed to the event by WebhookMetadata.shop == shop whose secret produced the HMAC over the delivered bytes`

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged internet user who is merely a legitimate (attacker-controlled) merchant of the app can cause the host application to process forged webhook data under another merchant's shop identity. Depending on how the host app's webhook handlers use `data.shop` (e.g. to look up and mutate that shop's stored session/state, issue actions, or write data keyed by shop), this enables cross-tenant data poisoning or state corruption without ever compromising the victim shop or leaking any credential. This matches the "cross-tenant access" impact category via a webhook-processing analog of the reported unsafe-trust-without-binding-validation bug class.

### Likelihood Explanation
Reasonably likely to be exploitable in practice: the attacker only needs to install the app on a shop they control (a normal, permission-less action), capture one webhook delivery, and replay it with a modified `shop-domain` header — no access to `api_secret_key`, tokens, or the victim's environment is required. The main mitigating factor is that the amount of exploitable damage depends entirely on how the host application's `WebhookHandler#handle` implementation trusts `data.shop`; the gem itself provides no protection against this specific misuse.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook_id`) header values in the HMAC-covered signable string, or otherwise cryptographically bind them to the signed payload, so that the shop attribute cannot be altered independently of the signature. At minimum, document prominently that `shop-domain` is unauthenticated and that host applications must cross-check it (e.g., against known installed shops) before trusting it for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no special privilege required).
2. Shopify delivers a legitimate webhook to the attacker's endpoint:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, `x-shopify-topic: orders/create`
   - Body: `raw_body`
3. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers; `HmacValidator.validate` recomputes HMAC over `raw_body` only [5](#0-4)  and it matches (since `raw_body` is unchanged) — validation succeeds.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...)` and invokes the handler [6](#0-5) , causing the host app to process attacker-controlled data as if it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
