Confirmed: `ShopifyAPI::Webhooks::Registry.process` at [1](#0-0)  validates the HMAC over `request.to_signable_string`, which is only the raw body (`@raw_body`), and then passes `request.shop` — read straight from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header — to the handler as the tenant identifier, without that header ever being covered by the signature.

### Title
Webhook tenant identity (`shop-domain` header) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [2](#0-1) , while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header [3](#0-2) . `HmacValidator.validate` only proves that the *body* bytes match a signature computed with the app's `api_secret_key` [4](#0-3) ; it says nothing about which shop the header claims to be from. `Registry.process` trusts the header value as the tenant identifier and hands it straight to the app's webhook handler [1](#0-0) .

### Finding Description
The identity binding that should hold is: `shop header value == shop that the signed body actually belongs to`. Because the HMAC is computed over `@raw_body` only, and the shop identifier lives in an HTTP header that is completely outside the signed material, this equality is never checked by the library. Any party capable of producing one valid `(raw_body, hmac)` pair for shop A (e.g., because they operate an app installation on shop A themselves, or capture one legitimate webhook delivery) can resend that exact same body/hmac pair while substituting an arbitrary `shopify-shop-domain` header value for shop B. `HmacValidator.validate` will still return `true` because it only recomputes the HMAC over the untouched body [5](#0-4) , and `Registry.process` will dispatch to the handler with `shop: request.shop` reporting the forged tenant [6](#0-5) . Any host application that follows this gem's documented pattern of using `data.shop` from the handler callback as the tenant/session key (as shown in the gem's own webhook documentation) [7](#0-6)  will process shop A's data under shop B's tenant context.

### Impact Explanation
This crosses a tenant boundary within the trust model this gem is meant to enforce: the whole purpose of HMAC-validating a webhook is to let the app safely determine "this payload came from Shopify for shop X." Since `shop` is unauthenticated relative to the signature, an attacker who controls or observes webhook traffic for their own installed shop can inject data attributed to a different merchant's tenant into the host application, i.e. cross-tenant data confusion/injection through the gem's own webhook verification API.

### Likelihood Explanation
Exploitation requires the attacker to already have at least one valid `(body, hmac)` pair signed with the app's `api_secret_key` — realistically obtained from a webhook delivered to their own shop's installation of the same app, which is available to any merchant who installs the app. No possession of `api_secret_key`, access tokens, or privileged access is needed; the header is fully attacker-controlled once the request reaches the app's webhook endpoint (`raw_body`/`headers` supplied by the caller as shown in the documented Rails controller integration) [8](#0-7) .

### Recommendation
Bind the shop identity into the signed material verified by `HmacValidator`, e.g. include the normalized `shop-domain` header (and ideally `topic`/`webhook-id`) in `to_signable_string`, or independently verify that the shop domain in the header matches a shop domain embedded/expected in the payload for topics where the payload includes it, before handing `shop` to the handler in `Registry.process`.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid signature of `B`).
2. Attacker replays the identical `(B, H)` pair to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes HMAC over `B` [5](#0-4) .
4. `Registry.process` calls the registered handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body `B` [6](#0-5) , causing the host app to process/store attacker data under the victim tenant.

### Citations

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

**File:** docs/usage/webhooks.md (L12-29)
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
    end
  end
end
```

**File:** docs/usage/webhooks.md (L127-135)
```markdown
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
