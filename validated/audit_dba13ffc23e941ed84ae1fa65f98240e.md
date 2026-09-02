### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the body bytes only, never the `shop-domain`, `topic`, `webhook-id`, or `api-version` values that the gem extracts straight from HTTP headers and hands to the app's webhook handler.

### Finding Description
`Request#hmac` reads the `X-Shopify-Hmac-Sha256` header, but `to_signable_string` is defined as just `@raw_body`: [1](#0-0) 

`HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it against the header-supplied HMAC: [2](#0-1) 

`Registry.process` treats a passing `HmacValidator.validate` as proof the whole request "did indeed come from Shopify" (per the gem's own docs) and then dispatches to the handler using the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`: [3](#0-2) [4](#0-3) 

The identity binding that is broken: `shop authenticated by HMAC` == `shop acted upon by the handler`. In reality, only `body` is bound to the HMAC; `shop` is an independent, attacker-controllable header value that is never cross-checked against anything the HMAC covers.

Critically, the webhook secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that has installed the app — it is not per-shop. Any unprivileged user can install the app on their own store (a normal, unprivileged action) and receive legitimate `(body, hmac)` pairs for their own webhook events. Because `hmac` only signs `body`, that captured `(body, hmac)` pair remains valid for the exact same body regardless of which `shop-domain` header is sent. The header is never bound to the signed bytes, so an attacker can then send a POST directly to the app's public webhook endpoint, reusing the legitimately obtained `(body, hmac)` pair while forging the `X-Shopify-Shop-Domain` header to name any other tenant of the same app.

### Impact Explanation
`HmacValidator.validate` returns `true` for this forged request because it only checks the body's HMAC, and `Registry.process` invokes the app's registered handler with `shop: request.shop` set to the attacker-chosen value: [5](#0-4) 

Since app handlers are documented and expected to key their business logic by `data.shop` (per `docs/usage/webhooks.md`), this allows one tenant's webhook payload to be misattributed to another tenant, i.e. cross-tenant data confusion/access — meeting the Critical "cross-tenant access" bar, entirely through this gem's own webhook-verification API.

### Likelihood Explanation
Any user who can install the target app on their own Shopify store (an ordinary, unprivileged action available to any Shopify user) can trigger webhooks for their own shop, capture a valid `(raw_body, hmac)` pair from their own legitimate webhook deliveries, and replay it to the app's public webhook endpoint with a spoofed `shop-domain` header for any other shop that uses the same app. No access to `api_secret_key`, access tokens, or the victim's credentials is required.

### Recommendation
Do not treat `HmacValidator.validate` as authenticating anything beyond the raw body. Either:
- Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable string used for HMAC verification (this would require Shopify's webhook signing to change, so more practically:
- Require/encourage the host app (and document explicitly) that `shop`, `topic`, and `webhook_id` from webhook headers must not be trusted for tenant identification without an out-of-band correlation (e.g., verifying the shop is a known, currently-installed shop and that the webhook wasn't already processed for a different shop), or
- At minimum, update `docs/usage/webhooks.md` to stop stating that `Registry.process`/`HmacValidator.validate` "verif[ies] the request did indeed come from Shopify" for the header-derived fields, since only the body is authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (unprivileged, self-service).
2. Attacker triggers an event (e.g., updates a product) causing Shopify to POST a webhook to the app's registered endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` (e.g., via their own server logs, or a proxy they control since it's their own installed app).
4. Attacker sends their own POST directly to the app's public webhook route with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it signs only `B`), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any `X-Shopify-Topic`/`X-Shopify-Webhook-Id` of their choosing.
5. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed and passed to `Registry.process`.
6. `Utils::HmacValidator.validate(request)` returns `true` (body/HMAC match).
7. `Registry.process` calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to act on `victim-shop.myshopify.com`'s tenant data/state using attacker-supplied content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L123-136)
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
```
