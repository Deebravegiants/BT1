Confirmed: `ShopValidator` is never used in the webhooks path, only in OAuth/token-exchange flows. This confirms the `shop` field on `ShopifyAPI::Webhooks::Request` has no additional validation and is not covered by the HMAC.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so the HMAC that `Utils::HmacValidator.validate` checks in `Registry.process` only authenticates the JSON body, never the `x-shopify-shop-domain` header that is read via `Request#shop` [2](#0-1)  and then trusted as the merchant identity passed to the app's handler [3](#0-2) .

### Finding Description
This is the same bug class as the TWAP oracle finding: a value that is acted upon (`token0`/`token1` ordering there, `shop` here) is not bound by the cryptographic check that is supposed to guarantee its authenticity (the pair's internal order there, the HMAC signature here).

`Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [3](#0-2) 

`Utils::HmacValidator.validate` computes the expected signature purely from `verifiable_query.to_signable_string` and compares it to `verifiable_query.hmac` [4](#0-3) . For `Request`, `to_signable_string` is hard-coded to the raw body only [1](#0-0) , while `shop` is pulled straight from the (attacker-controllable, unsigned) `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) .

Crucially, Shopify computes the webhook HMAC using the app's single shared `api_secret_key`/client secret — the same secret is used for every shop that has the app installed, not a per-shop secret. So any unprivileged user who can install the app on their own (e.g. free/dev) shop can trigger genuine webhook deliveries for that shop, capturing a fully valid `(body, hmac)` pair signed with the app's shared secret. Because `shop` is outside the signed payload, that same person can replay the identical body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value naming a different, victim shop. `Registry.process` will accept it — the HMAC still validates against the (unchanged) body — and will dispatch `WebhookMetadata` with `shop` set to the attacker-chosen victim domain to the app's handler, exactly as the library's own documentation instructs apps to trust it: `data.shop` is described as "The shop domain of the webhook" with no caveat [5](#0-4) , and the example handler uses it directly to key persisted/queued work: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) .

Notably, this codebase already has `ShopifyAPI::Utils::ShopValidator`, used to validate/sanitize shop domains in OAuth and token-exchange flows [7](#0-6) , but it is never applied to the webhook `shop` field, and there is no check at all in `Registry.process` binding `request.shop` to the signed content or to a known/installed shop.

### Impact Explanation
This breaks the identity binding "shop acted on == shop authenticated by the HMAC." An unprivileged internet user (anyone who can install the app on a shop they control — no special credentials, no leaked secrets, no access to the victim's tokens) can forge webhook events that the app attributes to an arbitrary victim shop domain string. Depending on how the host app uses `data.shop` (as documented, to key storage/queueing per merchant), this enables cross-tenant data injection/confusion — writing or triggering shop-scoped side effects under another tenant's identity. This matches the "cross-tenant access" Critical impact category.

### Likelihood Explanation
High. Exploitation only requires the attacker to install the target app on any shop they own (a normal, unprivileged action any developer can take), capture one legitimate webhook body+HMAC pair, and resend it with a modified `shop-domain` header — no cryptographic secrets need to be broken, since the header is simply outside the signed content.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) as part of the signed/verifiable content, or otherwise cryptographically/structurally bind `request.shop` to the HMAC-verified request — for example, require the caller to also verify that `request.shop` corresponds to a shop with a persisted session/installation before dispatching the handler, and document this requirement clearly. At minimum, `Registry.process` should not treat `request.shop` as trusted merchant identity based solely on the body HMAC.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed and
# receives a genuine Shopify webhook (any topic), giving them a valid body+HMAC:
body = '{"id":1,"note":"hi"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
# (This is exactly how Shopify itself signs the webhook to the attacker's own endpoint.)

# Attacker now POSTs the same body+HMAC to the app's webhook endpoint,
# but spoofs the shop-domain header to a victim shop they do not control:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HMAC validation succeeds (only body is checked) and the handler receives
# WebhookMetadata with shop == "victim-shop.myshopify.com", even though that
# shop never sent this webhook.
```

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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

**File:** lib/shopify_api/auth/token_exchange.rb (L1-1)
```ruby
# typed: strict
```
