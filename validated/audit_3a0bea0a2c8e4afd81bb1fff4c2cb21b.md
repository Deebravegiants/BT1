## Title
Webhook shop attribution is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values used to route and attribute the webhook to a specific merchant are taken from unauthenticated HTTP headers. An attacker who can obtain one genuine, validly-signed webhook body (e.g., by installing the app on their own shop) can replay that same body+HMAC pair against the app's public webhook endpoint while spoofing the `X-Shopify-Shop-Domain` header to any victim shop, causing the app to process attacker-controlled data as if it belonged to the victim tenant.

### Finding Description
The equality the gem is supposed to enforce is:
`bytes covered by the verified HMAC == bytes the handler acts upon for tenant attribution`.

In `lib/shopify_api/webhooks/request.rb`:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

only `@raw_body` is fed into the HMAC computation. Meanwhile `shop`, `topic`, and `webhook_id` are all read straight from HTTP headers with no cryptographic binding:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` only ever checks `verifiable_query.to_signable_string` against the HMAC:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` for tenant attribution immediately after this body-only check passes:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

This mirrors the reported bug class exactly: a field that is acted upon (here, the `shop` used to attribute/route webhook data to a specific merchant tenant) is not covered by the integrity check (the HMAC), which is instead computed over an unrelated, disjoint piece of data (the body only). Since a public app's `client_secret`/webhook signing secret is shared across every shop that installs it, any unprivileged attacker who installs the app on their own (even free/dev) shop receives genuine `(body, hmac)` pairs signed with the app's real secret. They can then submit an HTTP POST directly to the app's webhook endpoint, reusing their own valid body+HMAC but substituting the `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with an arbitrary victim shop domain. `HmacValidator.validate` will still succeed because it never inspects these headers, and `Registry.process` will hand the attacker's data to the host app's handler labeled as belonging to the victim shop.

### Impact Explanation
This breaks the tenant isolation the gem is supposed to guarantee for webhook processing: an unprivileged internet user (who only needs to be able to install the target public app once on any shop they control) can inject fabricated webhook events attributed to a different, victim merchant. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up the merchant's session/access token and act on their store, or to update per-shop state), this can lead to cross-tenant data corruption or trigger privileged actions against a shop the attacker does not control — matching the "cross-tenant access" High-severity category.

### Likelihood Explanation
Exploitation requires only: (1) the app be publicly installable (true for public/embedded Shopify apps), and (2) the app's webhook endpoint be reachable over the internet (a documented requirement for webhook delivery). No access token, `api_secret_key`, or privileged account is needed — only the ability to install the app once to harvest one valid signed payload and then replay it with forged headers.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived `shop` to the signed payload before it is trusted for attribution — e.g., include the `shop-domain`, `topic`, and `webhook-id` headers in `to_signable_string`, or verify the shop against an independently-known installed-shop list before dispatching to the handler.

### Proof of Concept
1. Install the target public app on an attacker-controlled shop `attacker.myshopify.com`; trigger any registered webhook topic to receive a real `(raw_body, X-Shopify-Hmac-Sha256)` pair signed by the app's genuine secret.
2. Send a POST request directly to the app's webhook callback endpoint using the captured `raw_body` and `X-Shopify-Hmac-Sha256` unchanged, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac` matches because `to_signable_string` only depends on `raw_body` — [1](#0-0)  — so `HmacValidator.validate` returns `true` — [5](#0-4) .
4. `Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"` and attacker-supplied `body`, even though the data actually originated from the attacker's own shop — [4](#0-3) .

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
