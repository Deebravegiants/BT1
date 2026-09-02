This confirms the vulnerability: the gem's `Registry.process` explicitly documents `data.shop` as the trusted "shop domain of the webhook" for the app to key its per-tenant logic (`docs/usage/webhooks.md:12-17,125`), while the actual `Utils::HmacValidator.validate` call only verifies `@raw_body` via `to_signable_string` [1](#0-0) , leaving `shop`, `topic`, and `webhook_id` — all read straight from HTTP headers — completely outside the signed payload [2](#0-1) .

### Title
Webhook tenant identity (`shop`) is read from an unsigned header while HMAC only covers the body, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, and `webhook_id` from raw HTTP headers, but the HMAC signature computed by `Utils::HmacValidator` only ever signs the JSON body (`to_signable_string` returns `@raw_body`). `Registry.process` trusts the header-derived `shop` value once the body's HMAC checks out, and passes it straight to the app's webhook handler as the tenant identifier.

### Finding Description
`Registry.process` performs exactly one check before dispatching to the app handler: `Utils::HmacValidator.validate(request)` [3](#0-2) . That validator recomputes an HMAC over `verifiable_query.to_signable_string` and compares it to the value in the `hmac-sha256` header [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is simply the raw request body [1](#0-0) .

However, the value that identifies *which tenant* the webhook is for — `shop` — along with `topic` and `webhook_id`, is pulled from separate, unsigned HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) via `shopify_header` [2](#0-1) , none of which are included in `to_signable_string`. This breaks the intended binding: `verified(body via HMAC) == identity acted upon (shop header)`. Any body+HMAC pair that is genuinely signed by Shopify for the app's `client_secret` (e.g. a webhook the attacker's own store legitimately receives) remains valid for **any** value placed in the `shopify-shop-domain` header, because that header is never part of the signed material.

This is the same bug class as the referenced report: a value the code treats as "earned"/"authoritative" for a given identity (there: auraBAL balance attributed to the caller of `_harvest()`; here: the `shop` attributed to the HMAC-verified payload) is not actually bound by the verification step that is supposed to authenticate it.

### Impact Explanation
The gem's own documentation instructs host apps to key per-tenant work off `data.shop` after calling `Registry.process` (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) . An attacker who operates their own shop installed on the app receives genuinely-signed webhooks for their own store. By resending that exact body (and its still-valid HMAC) to the app's webhook endpoint while swapping only the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header to name a victim shop, the request still passes `HmacValidator.validate` and is dispatched to the handler tagged with the victim's shop domain. Since apps typically use `data.shop` to select which tenant's session/records to update (mandatory topics like `customers/redact`, `shop/redact`, and ordinary business webhooks alike), this is a cross-tenant identity-binding break: the app can be made to process a "webhook" it will attribute to a shop that neither sent it nor authorized it, without the attacker ever possessing that victim's credentials.

### Likelihood Explanation
Requires only an unprivileged attacker who has installed the app on their own (attacker-controlled) shop — a normal, unprivileged capability — and the ability to POST arbitrary headers to the app's public webhook endpoint, which is by definition internet-reachable. No `api_secret_key`, access token, or victim credentials are needed.

### Recommendation
Include the identity fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material, or otherwise cryptographically bind them to the verified body (e.g., have `to_signable_string` incorporate the header values, or require the host application to cross-check `shop` against session/tenant state established via OAuth before trusting it), so that the HMAC verification actually authenticates the identity the request claims.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. `orders/create`, with a valid `X-Shopify-Hmac-Sha256` header computed over the JSON body using the app's `client_secret`.
2. Attacker replays the identical raw body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unmodified) body [1](#0-0) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: ..., ...)` [6](#0-5) , and the host app performs tenant-scoped work believing it originated from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```
