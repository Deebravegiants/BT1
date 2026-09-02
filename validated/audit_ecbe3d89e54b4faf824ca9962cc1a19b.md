This confirms the finding. The gem's documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0)  and then hands `data.shop` to the app's handler as a trusted tenant identifier [2](#0-1) , but the HMAC computed by `HmacValidator` only covers the raw body, not the `shop-domain` header.

### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates that the body bytes were signed by the app's secret, but the `shop-domain` header used as the tenant identity key is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook exclusively via `Utils::HmacValidator.validate(request)` [3](#0-2) . That validator computes the HMAC over `verifiable_query.to_signable_string` [4](#0-3) , and for `Webhooks::Request` that signable string is defined as just the raw body:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [5](#0-4) 

Meanwhile, `shop` is read directly and unauthenticated from the `shopify-shop-domain` header:
```ruby
sig { returns(String) }
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [6](#0-5) 

That unauthenticated `shop` value is then propagated directly into the object passed to the app's webhook handler as the tenant key, with no cross-check against the signed body:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [7](#0-6) 

Because every shop that installs the app shares the *same* `api_secret_key`, any HTTP webhook that Shopify legitimately delivers to the app (for the attacker's own shop, or any shop the attacker controls/subscribes to) is signed with the identical secret used for every other tenant. `HmacValidator.validate` proves only `computed_signature(body) == received_signature`; it never checks the equality `signed_shop == header_shop`. An attacker who captures one genuine `(body, hmac)` pair from a webhook delivered to their own shop can replay that exact `body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header value with a victim shop's domain. The HMAC check still passes (it never saw the header), and `Registry.process` forwards `shop: <victim-domain>` to the handler as if the data belonged to that victim tenant.

### Impact Explanation
This breaks the identity binding `signed_bytes == authenticated_shop`. The `shop` field is acted upon (used by every downstream handler as the row/session key to decide whose data is being processed — see the documented handler example calling `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [8](#0-7) ) but is not covered by the HMAC. This is a cross-tenant integrity issue: attacker-controlled webhook content can be attributed to another merchant's tenant, matching the "Critical - cross-tenant access" impact bucket, since any host application that (as the gem's own documented handler pattern shows) uses `data.shop` to select the tenant record/session to write into is misled into applying attacker data under a victim shop's identity.

### Likelihood Explanation
Exploitation requires only an unprivileged internet user who can install the target app on their own (attacker-controlled) shop — a normal, unprivileged action any merchant/developer can take — to receive at least one genuinely signed webhook, then replay the body+HMAC with a forged `shop-domain` header to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is required; this is directly reachable through the gem's own `Webhooks::Request`/`Registry.process` API exactly as documented.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook_id`) header values in the HMAC-signed material, or independently verify that `request.shop` matches a shop the app has an active, previously-established session/webhook registration for before invoking the handler, rather than trusting the header value implicitly once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook (e.g. `orders/create`).
2. Shopify delivers a legitimate webhook to the app's callback URL with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of body>`, and some JSON body.
3. Attacker captures this `(raw_body, hmac)` pair.
4. Attacker crafts a new HTTP POST to the same webhook endpoint, reusing the identical `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers [9](#0-8) ; `Registry.process` calls `HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only and matches, since the body/HMAC pair is unchanged [3](#0-2) .
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and the host application (following the gem's own documented pattern) processes/queues this data as belonging to the victim shop's tenant.

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L45-60)
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

```
