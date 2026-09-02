### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop impersonation - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity via `Utils::HmacValidator.validate`, but the signable string used for that HMAC check is only the raw request body. The `shop` (and `topic`, `api_version`, `webhook_id`) values are read from separate, unauthenticated HTTP headers that are never included in the signed content, so the binding "authenticated shop == shop acted upon" is broken, mirroring the reported bug class of "a field acted on but not covered by the HMAC."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `#shop` is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is attacker-controllable HTTP input, not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC (over the body only) and then trusts `request.shop` to build `WebhookMetadata`, which is handed directly to the app's handler as the tenant identifier for the webhook event: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the HMAC purely against `verifiable_query.to_signable_string` (the body, in this case) and the app's `api_secret_key`: [4](#0-3) 

Because the HMAC secret (`api_secret_key`) is shared across all shops that have installed the app (it is not shop-specific), a merchant who has legitimately installed the app receives real webhook deliveries for their own shop with a valid `(body, hmac)` pair signed by that shared secret. Since the `shop-domain` header is excluded from the signed content, that same merchant can resend the identical body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a different shop's domain. `HmacValidator.validate` still succeeds (it never inspected the header), and `Registry.process` will invoke the app's webhook handler believing the event belongs to the victim shop: [5](#0-4) 

The documented handler contract explicitly treats `data.shop` as the trusted tenant key for the event, e.g. used to enqueue tenant-scoped background jobs: [6](#0-5) 

The equality this breaks: `shop authenticated by the HMAC` should equal `shop the webhook is attributed to and acted upon`. In reality: `shop covered by signature == {}` (nothing) while `shop used by the handler == header value chosen entirely by the sender`.

### Impact Explanation
This is a cross-tenant confusion vulnerability: any party that operates one instance of the app (i.e. any merchant who installs it, which requires no special privilege beyond normal app installation) can produce a validly-HMAC'd webhook payload for their own shop and then relabel it as belonging to an arbitrary other shop domain when delivering it to the app's public webhook endpoint. Any host application that follows this gem's documented contract (using `data.shop` as the tenant key, per `docs/usage/webhooks.md`) will process attacker-supplied data under another tenant's identity — for example enqueuing "orders/create" data or triggering data mutation/deletion webhooks (e.g. `app/uninstalled`, `shop/redact`) attributed to a shop the attacker does not own. This satisfies the "Critical – cross-tenant access" impact bar since it lets one tenant's authenticated traffic be reattributed to another tenant without needing the app's `client_secret`, an access token, or any credential belonging to the victim shop.

### Likelihood Explanation
Likelihood is high for any app built on this gem that relies on `WebhookMetadata#shop` for tenant scoping (which is the sole documented mechanism the gem provides). The attacker only needs: (1) to install the target app on their own shop (a normal, low-privilege action), (2) capture one legitimate webhook delivery (attacker controls their own endpoint), and (3) replay the body+HMAC to the app's real webhook endpoint with a forged `shop-domain` header. No knowledge of `api_secret_key`, no stolen tokens, and no interaction with the victim shop are required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` value to the verified payload before it is handed to `WebhookMetadata`/handlers. At minimum, document and enforce that `shop` must be independently corroborated against a known/installed shop record before being trusted as a tenant key, since the current signature only proves body integrity, not the origin shop.

### Proof of Concept
1. App merchant "Attacker" installs the target Shopify app on their own store `attacker-shop.myshopify.com` and configures a webhook receiver they control to intercept a real delivery for topic `orders/create`.
2. Attacker captures the legitimate raw body and its `x-shopify-hmac-sha256` value from that delivery — both were computed/signed by Shopify using the app's shared `api_secret_key`, over the body only: [7](#0-6) 
3. Attacker sends a new HTTP POST to the app's real webhook endpoint with the identical raw body and `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present): [8](#0-7) 
5. `Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks the body against the shared secret: [9](#0-8) 
6. The registered handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)`, where `request.shop` is `"victim-shop.myshopify.com"` — data attacker fully controls: [10](#0-9) 
7. Any downstream logic keyed on `data.shop` (as shown in the gem's own documented handler example) now processes/attributes the attacker's payload as belonging to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** docs/usage/webhooks.md (L10-29)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

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
