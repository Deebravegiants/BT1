This confirms the core issue: the docs explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and that `data.shop` is documented as trustworthy — "The shop domain of the webhook" [2](#0-1)  — establishing that the gem's own contract treats `shop` as verified, when in fact it is not covered by the HMAC.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing tenant misattribution of otherwise-valid webhook payloads - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-validating the raw request body, but the `shop` value handed to the application's handler is read directly from the unauthenticated `X-Shopify-Shop-Domain` header. This breaks the binding "bytes verified versus bytes parsed": the signature covers only `@raw_body`, while the shop identity that the host application uses as its tenant key is parsed independently and never checked against the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) . The `shop` accessor is populated straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to that value: [4](#0-3) .

`Registry.process` validates only the HMAC of the request (i.e., of `raw_body`) and then immediately trusts `request.shop` to build the metadata passed to the app's handler: [5](#0-4) .

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (body only) and secure-compares it against the `hmac` header value: [6](#0-5) . Nothing in this path ties the verified body to the specific shop header that accompanies it.

Because the same `api_secret_key` HMAC secret is shared across every shop that has installed the app (it's a single per-app secret, not per-shop), any body+HMAC pair that Shopify legitimately produced for one webhook delivery is a *valid* HMAC for that exact body regardless of which shop header is attached to the request. A user in control of network traffic to the app's public webhook endpoint (e.g., anyone who can send raw HTTP requests to it — no privileged token needed) can take a captured, valid `(raw_body, hmac)` pair and resend it with a different `X-Shopify-Shop-Domain` header. `Registry.process` will accept it because the HMAC check only validates the body, and will invoke the app's handler claiming the payload belongs to the attacker-chosen shop: [5](#0-4) . The documentation itself instructs developers to key their business logic (e.g., `shop_domain: data.shop`) off this unauthenticated field, treating `Registry.process` as if it fully "verifies the request did indeed come from Shopify": [7](#0-6) , [1](#0-0) .

### Impact Explanation
This is a cross-tenant integrity break: a webhook payload cryptographically proven to originate from the app's own secret can be relabeled to any other shop domain the attacker chooses, causing the host application to apply shop-A's data/events under shop-B's tenant record (e.g., writing order/product state, revoking/altering data, or triggering side effects scoped by `data.shop`). This matches the Critical "cross-tenant access" impact category, since the gem's authentication primitive for webhooks fails to bind the one piece of tenant-identifying data (`shop`) that the rest of the API surface, and the gem's own documentation, assume is authenticated.

### Likelihood Explanation
Exploitation requires only: (1) network reachability to the app's public webhook receiver endpoint (a public, unauthenticated URL by design), and (2) knowledge of one valid `(raw_body, hmac)` pair for the target app — obtainable, for instance, by an attacker who is themselves a legitimate merchant of the app and can trigger/observe a webhook delivery to infrastructure they control (e.g., temporarily pointing/observing their own webhook subscription, or via a shared secret being reused for their own store's deliveries), since the same secret and validation logic apply to every shop. No `api_secret_key`, access token, or elevated privilege is required to perform the replay against the victim shop.

### Recommendation
Bind the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values into the HMAC-verified signable content, or otherwise cryptographically tie the shop identity to the verified body — e.g., include them in `to_signable_string`, or independently validate `shop` against a known/registered shop list plus reject if the same body+hmac pair is replayed with a different shop header. At minimum, document that `shop` is not authenticated by `Registry.process`'s HMAC check and require host applications to cross-check it against their own installed-shop registry before trusting `data.shop`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a valid, unprivileged installation, no special access required).
2. Attacker triggers or otherwise obtains a legitimate webhook delivery `(raw_body, X-Shopify-Hmac-Sha256: H)` for their own shop — `H` is computed by Shopify with the app's single shared `api_secret_key`, per `HmacValidator.compute_signature`: [8](#0-7) .
3. Attacker sends a POST to the app's webhook endpoint with the same `raw_body` and `hmac` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against `H`: [9](#0-8) .
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop == "victim-shop.myshopify.com"`, even though the body/content actually originated from `attacker-shop.myshopify.com`'s webhook delivery: [10](#0-9) .
6. The host application processes attacker-controlled data under the victim shop's tenant context.

### Citations

**File:** docs/usage/webhooks.md (L10-26)
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
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L33-40)
```ruby
        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
