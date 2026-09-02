### Title
Webhook `shop`, `topic`, and `webhook_id` Fields Are Not Covered By HMAC Validation, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature verified by `Utils::HmacValidator.validate` binds solely to `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read from attacker-controllable HTTP headers — are never part of the signed material, yet `Registry.process` trusts them and forwards `request.shop` directly to the app's webhook handler as the tenant identity.

### Finding Description
`Webhooks::Request` derives its verifiable fields from headers, but only the body is bound to the HMAC: [1](#0-0) 

Concretely:
```ruby
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end

def shop
  T.cast(shopify_header("shop-domain"), String)
end

def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` i.e. `HMAC(secret, raw_body)` only, and then, without any additional binding, passes `request.shop` (an unauthenticated header value) into the `WebhookMetadata` handed to the app's handler: [2](#0-1) 

The identity equation the gem should guarantee is:
`shop attributed to handler == shop that Shopify actually signed the webhook for`

But because `shop` (and `topic`, `webhook_id`, `api_version`) is excluded from `to_signable_string`, the equation only holds as: `HMAC(secret, raw_body) == received_hmac`, with `shop` completely decoupled from that check.

### Impact Explanation
Any party that has captured one legitimate `(raw_body, hmac)` pair produced by Shopify for the app (e.g. a webhook delivered to their own shop, or any historical valid delivery) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value. `Utils::HmacValidator.validate` will still return `true` because it only ever hashes `@raw_body`. `Registry.process` will then invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen shop domain, causing the host application to process/attribute webhook data (including mandatory topics like `shop/redact` and `customers/data_request`) under an arbitrary victim tenant. This is a cross-tenant identity-confusion vulnerability at the gem's own API boundary (`Registry.process`/`WebhookMetadata`), not a case of an app ignoring documented guidance — the gem itself hands out an unauthenticated `shop` field to the trusted callback after "validating" the request.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one valid `(body, hmac)` pair for the target app (trivially available if the attacker's own shop installs the app and receives any webhook, since webhook bodies/HMACs for a given app share the same `client_secret` across all shops). No access token, `api_secret_key`, or privileged access is required — only the ability to send an HTTP POST to the app's public webhook endpoint with forged headers, which is exactly the "unprivileged internet user" scenario.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` (or at minimum `shop`) in the signable string used for HMAC verification, or otherwise cryptographically bind the header-derived identity fields to the signed payload before they are surfaced to `WebhookMetadata`. Failing that, document loudly that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must be independently verified against the caller's own session/shop store before being trusted for tenant attribution.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and has installed the victim's app,
# so they legitimately receive one webhook delivery with a valid HMAC for some body.
captured_body = '{"id":1}'
captured_hmac_b64 = "<hmac captured from a real Shopify webhook delivery>"

# Replay the exact same body/HMAC but claim to be from the victim shop.
forged_headers = {
  "x-shopify-topic" => "shop/redact",
  "x-shopify-hmac-sha256" => captured_hmac_b64,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # arbitrary, attacker-controlled
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)

# Passes: HMAC only ever covers raw_body, never the shop header.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

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
