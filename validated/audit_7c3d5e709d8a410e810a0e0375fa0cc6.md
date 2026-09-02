Confirmed the finding. The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`), and the `shop` field is documented as the identifier apps should key their tenant logic on (`docs/usage/webhooks.md:14, 26`), yet the HMAC only ever covers `@raw_body` [1](#0-0) , and `shop`/`topic`/`webhook_id` are read straight from unauthenticated headers [2](#0-1) .

### Title
Webhook tenant identity (`shop-domain` header) is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before dispatching to the app's handler with the shop's identity attached [3](#0-2) . In practice, the HMAC check only authenticates the raw body bytes; the `shop` (tenant identifier), `topic`, `webhook_id`, and `api_version` are taken from HTTP headers that are completely excluded from the signed content.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Registry.process` validates only that string against the HMAC header: [4](#0-3) 

`HmacValidator.validate_signature` recomputes the HMAC purely from `to_signable_string` (i.e. the body) and the app's `api_secret_key`: [5](#0-4) 

Meanwhile `shop`, `topic`, and `webhook_id` — none of which are part of the signed bytes — are read verbatim from attacker-controllable headers: [6](#0-5) 

The binding this breaks, expressed as an equality that the gem fails to enforce: `shop` (the tenant used by `WebhookMetadata` and thus by the host app's business logic) must equal `shop_that_produced(hmac, body)`, but the gem only proves `hmac == HMAC(api_secret_key, body)` — it never proves the `shop` header is the shop Shopify actually sent that body for. Since a single `api_secret_key` is shared by the app across all of its installed shops, any valid `(body, hmac)` pair — which is not secret and is routinely visible to the shop's own staff/apps that receive it, to intermediate proxies/logs, or to anyone able to replay a POST to the app's public webhook endpoint — can be resubmitted with the `shop-domain`/`x-shopify-shop-domain` header rewritten to name a *different* shop the same app serves. `Registry.process` will still accept it as valid and hand the handler a `WebhookMetadata` whose `shop` is attacker-chosen while `body`/`hmac` were genuinely signed for another tenant [7](#0-6) .

Because host apps are told by this gem's own documentation to key their downstream logic off `data.shop` (e.g. enqueuing jobs, loading the correct merchant's offline session, writing to the correct tenant's DB row) [8](#0-7) , this gap lets one merchant using a shared multi-tenant app cause another merchant's webhook payload to be misattributed to their own shop, or attribute their own crafted webhook body to a victim shop — a cross-tenant confusion the gem's "verify the request came from Shopify" contract is supposed to prevent.

### Impact Explanation
This is a cross-tenant identity-binding break: the gem asserts webhook authenticity but that assertion says nothing about which tenant (`shop`) the authenticated bytes belong to. Any downstream logic trusting `WebhookMetadata#shop` (as the gem's docs instruct) can be tricked into applying one shop's data/events under another shop's identity, which is a cross-tenant access/data-integrity violation for multi-shop apps sharing one `api_secret_key`.

### Likelihood Explanation
Requires only: (1) an unprivileged party who can observe or capture one legitimately-signed `(body, hmac)` pair sent to the app's public webhook endpoint for any shop on the app (trivial for a merchant receiving their own genuine webhooks, or via network capture since webhook delivery is plain HTTPS POST to a URL the app operator chooses, sometimes proxied/logged), and (2) the ability to POST that same body/hmac with a different `shop-domain` header to the same public endpoint. No `api_secret_key`, access token, or privileged account is needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, or otherwise cross-check the header-derived `shop` against an independent source of truth (e.g., verify the shop is one for which the app has an active, previously-established session/webhook subscription record with a matching `webhook_id`, rather than trusting the header alone). At minimum, document prominently that `Registry.process`'s HMAC check only proves body integrity/authenticity, not the authenticity of the `shop`, `topic`, or `webhook_id` headers, so host apps do not treat `WebhookMetadata#shop` as cryptographically bound.

### Proof of Concept
1. App `A` is installed on shops `victim.myshopify.com` and `attacker.myshopify.com`, sharing one `api_secret_key`.
2. Attacker's own shop legitimately receives a webhook: raw body `B` with a valid `x-shopify-hmac-sha256` header `H = HMAC-SHA256(api_secret_key, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker POSTs to the app's public webhook endpoint the same `B` and `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this successfully [9](#0-8) ; `HmacValidator.validate` returns `true` because it only checks `B` against `H` [10](#0-9) .
5. `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` and the attacker's own body content [4](#0-3) , causing the app to process attacker-controlled data under the victim shop's tenant identity.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

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
