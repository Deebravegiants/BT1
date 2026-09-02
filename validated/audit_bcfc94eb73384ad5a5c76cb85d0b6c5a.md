### Title
Webhook shop-domain header trusted for tenant identity without HMAC coverage - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw request body only, while the shop identity (`x-shopify-shop-domain`), topic, and webhook-id are read straight from unauthenticated HTTP headers and handed to the app's webhook handler as if they were verified. This breaks the equality that should hold after HMAC validation: `authenticated_shop == shop_acted_upon`. In practice, `verified_body == true` does not imply `header_shop == originating_shop`.

### Finding Description
`Utils::HmacValidator.validate` only checks the HMAC against `verifiable_query.to_signable_string`, and for webhooks that string is defined as just the raw body: [1](#0-0) [2](#0-1) 

```ruby
sig { override.returns(String) }
def hmac
  Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
end
...
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

The `shop`, `topic`, and `webhook_id` fields are parsed from HTTP headers and are never included in the signed payload: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC (over the body only) and then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the metadata passed into the app's handler: [4](#0-3) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

This is exactly the bug class described in the analog report: a field that is *acted on* (the shop the event is attributed to) is not covered by the cryptographic check that gates the action (the HMAC over the body). Compare this to `Auth::Oauth::AuthQuery#to_signable_string`, which correctly includes `shop` in the signed payload for the OAuth callback: [5](#0-4) 

The webhook path has no equivalent binding of `shop` into the signature.

### Impact Explanation
An unprivileged internet user who controls (or has installed the app on) any single shop legitimately receives real, correctly signed webhook deliveries from Shopify for that shop — HMAC included. Because that HMAC only covers the JSON body and not the `shop-domain` header, the attacker can capture one such (body, HMAC) pair and replay it directly to the app's public webhook endpoint while substituting a different `x-shopify-shop-domain` header value naming a victim shop. `HmacValidator.validate` will still succeed (the body/HMAC pair is valid), and `Registry.process` will forward `WebhookMetadata` claiming the event originated from the victim shop. Any host application that trusts `WebhookMetadata#shop` from a "verified" webhook (as the documented API implies it should) to look up sessions, update local records, or trigger tenant-scoped side effects can be made to attribute attacker-controlled event data to a different tenant — a cross-tenant data-integrity/confusion issue reachable without any credentials, tokens, or `api_secret_key` access.

### Likelihood Explanation
High reachability: any actor who can install the app on a shop they control (or otherwise receive one legitimate webhook) obtains a valid (body, HMAC) pair for arbitrary well-formed JSON bodies of their choosing (since body content is fully under the shop owner's control for many topics, e.g. `products/update`, `orders/create` on their own store), and the webhook endpoint is a public HTTP endpoint by design. No secret material is required to mount the replay; only header rewriting.

### Recommendation
Bind the shop identity (and ideally topic/webhook-id) into the value that is HMAC-verified, or otherwise independently authenticate the `shop-domain` header before trusting it — e.g., include the `x-shopify-shop-domain` header in the signable string used by `Request#to_signable_string`/`HmacValidator`, or require the host application to cross-check `request.shop` against a shop it has an active, previously-established session/install record for before acting on the payload. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted as a tenant identifier on its own.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. updates a product), causing Shopify to POST a legitimately HMAC-signed body `B` with header `x-shopify-shop-domain: attacker-shop.myshopify.com` to the app's public webhook URL.
2. Attacker captures `B` and its `x-shopify-hmac-sha256` value.
3. Attacker replays the exact same request to the same public webhook URL, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or `x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC (`lib/shopify_api/utils/hmac_validator.rb`), and `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`.
5. Any handler logic keyed on `data.shop` (e.g. "look up victim's session/store and apply this update") now operates on attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
