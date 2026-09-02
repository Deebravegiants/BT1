This confirms the finding: the docs explicitly document `data.shop` in `WebhookMetadata` as "The shop domain of the webhook" (docs/usage/webhooks.md line 14) that host apps use for tenant routing (as shown in the doc's own example calling `perform_later(topic: data.topic, shop_domain: data.shop, ...)` at line 26). Yet the HMAC signature only ever covers `raw_body` — the `shop` field is read straight from a header that is entirely outside the signed bytes.

### Title
Webhook `shop` identity is trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `api_version`, `webhook_id`) values straight from HTTP headers, while `to_signable_string` — the value that `HmacValidator` actually verifies — is only the raw request body. `Registry.process` accepts any request whose HMAC over the body is valid and then hands the *unverified* `shop` header straight to the app's handler as trusted tenant identity, breaking the binding `shop-authenticated == shop-that-produced-the-signed-bytes`.

### Finding Description
`Registry.process` validates the webhook exclusively via: [1](#0-0) 
which calls `Utils::HmacValidator.validate(request)`. That validator computes/verifies the signature only against `verifiable_query.to_signable_string`: [2](#0-1) 
And `Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 
Meanwhile `Request#shop` is read straight off the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never part of the signable string: [4](#0-3) 
After the HMAC check passes, `process` forwards this unverified `shop` straight into `WebhookMetadata`, which the host application's handler is documented to trust as "the shop domain of the webhook": [5](#0-4) [6](#0-5) [7](#0-6) 

The identity binding the gem is supposed to enforce is: `shop acted on by the handler == shop that produced the HMAC-signed bytes`. Because the signed bytes are only the body (never the shop header), that equality is not actually checked anywhere in this gem — it merely checks `hmac(secret, body) == received_hmac`, independent of which `shop-domain` header accompanies that body.

An unprivileged internet user can obtain a valid `(body, hmac)` pair for arbitrary content by creating a free/dev Shopify store, installing the target app, and triggering any webhook topic the app subscribes to (e.g. `orders/create`) — Shopify will send a correctly HMAC-signed request for that attacker-owned shop. The attacker captures this `(raw_body, x-shopify-hmac-sha256)` pair and replays it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `Registry.process` will still find the HMAC valid (it was never influenced by the shop header) and will invoke the app's handler with `data.shop` == the victim's domain, while `data.body` contains the attacker's own data.

### Impact Explanation
If a host application uses `data.shop` from `WebhookMetadata` — exactly as the gem's own documentation instructs (`shop_domain: data.shop`) — to select which tenant's/merchant's records to create, update, or key a background job against, an attacker can inject attacker-controlled webhook payloads that are processed under another merchant's identity. This is a cross-tenant data-integrity/confusion issue: data ostensibly belonging to shop A gets attributed to and processed against shop B's tenant context, without the attacker needing any credential belonging to shop B.

### Likelihood Explanation
Likelihood is bound by the requirement to know/guess a target shop's exact `myshopify.com` domain (often discoverable or guessable) and to have a body payload that will be processed meaningfully for the target's tenant context (e.g., a topic/schema that doesn't require shop-specific IDs to have effect, such as `shop/redact`, `app/uninstalled`, or metadata-only topics). Any internet user can become a "sender" of legitimately-signed webhooks by registering a free Shopify development store and subscribing the target app — no privileged credentials, TLS interception, or leaked secrets are required.

### Recommendation
Include the `shop` (and ideally `topic`/`api_version`/`webhook_id`) header value in the HMAC-signed data, or independently bind/verify it — for example, by validating `shop` against a known/allow-listed set of installed shops for that HMAC-secret scope, or by requiring the caller to pass the expected shop and comparing it before dispatching to the handler in `Registry.process`. At minimum, document prominently that `data.shop` is unauthenticated header data and must not be trusted for tenant selection without additional verification (e.g., cross-checking against a stored session for that shop).

### Proof of Concept
```ruby
# 1. Attacker registers a free/dev Shopify store "attacker-shop.myshopify.com",
#    installs the target app, and triggers a webhook the app is subscribed to
#    (e.g. orders/create). Shopify sends:
#
#    POST /webhook
#    x-shopify-topic: orders/create
#    x-shopify-hmac-sha256: <valid HMAC of raw_body using app's real api_secret_key>
#    x-shopify-shop-domain: attacker-shop.myshopify.com
#    <raw_body>

# 2. Attacker captures raw_body and the x-shopify-hmac-sha256 header, then replays
#    the exact same body + hmac to the app's webhook endpoint but rewrites the
#    shop header:
#
#    POST /webhook
#    x-shopify-topic: orders/create
#    x-shopify-hmac-sha256: <same, still valid HMAC>
#    x-shopify-shop-domain: victim-shop.myshopify.com
#    <same raw_body>

# 3. In the gem:
request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# -> Utils::HmacValidator.validate(request) is TRUE, because it only checks
#    OpenSSL::HMAC.hexdigest(secret, request.to_signable_string) == request.hmac
#    and to_signable_string == raw_body only.
# -> handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
#    is invoked, even though this payload never actually originated from
#    victim-shop.myshopify.com.
```

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
