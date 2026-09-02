## Analog Finding Identified

The reported bug class — an unbound field that is *processed* by the code but not *covered* by the authenticity check — has a direct analog in this gem's webhook-processing path: the `shop` (and `topic`/`webhook_id`/`api_version`) values are read straight from unauthenticated HTTP headers, while the HMAC that is validated only covers the raw request body.

### Title
Webhook `shop` (and other identity metadata) is read from unauthenticated headers and is never covered by the HMAC check, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , and `HmacValidator.validate` verifies the HMAC solely against that signable string [2](#0-1) . However, `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all pulled directly from HTTP headers that are never part of the signed payload [3](#0-2) . `Registry.process` validates the HMAC and then trusts `request.shop` as the tenant identity forwarded to the app's handler [4](#0-3) .

### Finding Description
The identity binding that should hold is:
`shop that produced/authorized the signed payload == shop attributed to the delivered webhook event`

In this gem that equality is not enforced. The HMAC secret used to sign webhooks is the app's single `api_secret_key`/`old_api_secret_key`, shared across every merchant shop that has installed the app [5](#0-4) . Since the signature covers only `@raw_body` and not the `x-shopify-shop-domain` (or `shopify-shop-domain`) header [1](#0-0) , any attacker who has legitimate access to *one* shop that has installed the target app (e.g. by installing it on their own free/dev store) can:

1. Trigger a legitimate webhook for their own shop and capture the raw request body plus its valid `x-shopify-hmac-sha256` value.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with a victim shop's domain.

`HmacValidator.validate` will succeed (the body and secret are unchanged), and `Registry.process` will hand the handler a `WebhookMetadata` object whose `shop` field is the attacker-chosen victim domain, with `topic`/`body` fully attacker-controlled [6](#0-5) . The documented handler pattern shows apps are expected to key their processing (e.g. background jobs, data writes, session lookups) directly off `data.shop` [7](#0-6) .

### Impact Explanation
This breaks the tenant boundary the library is expected to guarantee: it lets an unprivileged internet user (any developer who can install the app once) forge webhook events — including sensitive lifecycle topics such as `app/uninstalled` or `shop/redact` — and have them delivered under the identity of a completely different, victim shop. Any host application that follows the library's documented pattern of trusting `data.shop` for tenant-scoped processing (session revocation, data deletion, job dispatch) is exposed to cross-tenant interference. This matches the "cross-tenant access" Critical-impact category since the attacker crosses the tenant/shop boundary using only the shared app secret they never needed to see.

### Likelihood Explanation
Likelihood is high: it requires no leaked credentials or privileged access — only that the attacker install the target app on any shop they control (a normal, permitted action for any Shopify Partner/dev store), then replay a captured request with one header changed. No cryptographic material needs to be broken because the header in question was never part of the signed data.

### Recommendation
Bind the shop identity into the authenticity check: `Request#to_signable_string` should not be the only trust anchor for `shop`; instead, the library (or its documentation) must require verifying that `request.shop` corresponds to a shop actually known/installed by the app (e.g. cross-check against stored sessions) before treating the webhook as authoritative for that shop, or Shopify-side, ensure the header is included in the HMAC computation. At minimum, the gem should not present `request.shop` as trustworthy metadata without this caveat.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) and capture the raw POST body `B` and header `x-shopify-hmac-sha256: H`.
2. Send a new POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `x-shopify-hmac-sha256: H` (unchanged, still validates because it only signs `B`)
   - `x-shopify-shop-domain: victim.myshopify.com` (attacker-chosen)
   - `x-shopify-topic`, `x-shopify-webhook-id` optionally changed to any registered topic.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (only `B` and the shared secret matter) [5](#0-4) ; `Registry.process` invokes the registered handler with `WebhookMetadata.shop == "victim.myshopify.com"` [6](#0-5) , even though the event body and hmac originated from the attacker's own shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** docs/usage/webhooks.md (L19-29)
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
