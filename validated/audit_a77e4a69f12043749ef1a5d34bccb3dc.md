### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is validated by `Utils::HmacValidator` against `to_signable_string`, which returns only the raw request body. `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers and are never part of the signed content, yet `Webhooks::Registry.process` forwards them unchecked to the app-supplied handler as authenticated metadata.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, `#api_version` are pulled straight from headers with no cryptographic binding to the signature: [2](#0-1) 

`HmacValidator.validate` verifies the HMAC solely over `verifiable_query.to_signable_string` (the body): [3](#0-2) 

`Registry.process` treats a valid body-HMAC as proof of the whole request's authenticity, then builds `WebhookMetadata` straight from the unauthenticated header fields and hands it to the app's handler: [4](#0-3) 

The equality the gem implicitly claims to hold is:
`shop authenticated by HMAC verification` == `shop delivered to the handler as data.shop`

In reality: `HMAC covers only raw_body` while `data.shop / data.topic / data.webhook_id / data.api_version come from unauthenticated x-shopify-* headers`. This is exactly the class of "field acted on but not covered by the HMAC" bug described in the reference report — the assembly bug fails to bind the actual overflow condition to the checked condition, and here the gem fails to bind the tenant identity actually verified (the body's authenticity) to the tenant identity exposed to application logic (the header-derived `shop`).

The library's own documented usage pattern encourages apps to trust `data.shop` directly after `Registry.process` succeeds: [5](#0-4) 

### Impact Explanation
An unprivileged internet user who can install the target app on their own (even free/dev) Shopify store legitimately receives real webhook deliveries with a valid `x-shopify-hmac-sha256` for their own store's body content. Because the signature never binds to the `shop` header, the attacker can replay that exact `(raw_body, hmac)` pair to the app's shared webhook endpoint while substituting the `shopify-shop-domain` header with a victim merchant's domain. `HmacValidator.validate` still passes (it only checks the body), and `Registry.process` constructs `WebhookMetadata` reporting the victim's shop with attacker-controlled body content. Any app that keys its persistence/business logic off `data.shop` (as the gem's own documentation instructs) will attribute attacker-supplied data to another merchant's tenant — a cross-tenant data injection/confusion crossing the tenant boundary without any credential belonging to the victim.

### Likelihood Explanation
Likelihood is moderate: it requires the attacker to be an app user (achievable by installing the target public app on a store they control, no special privilege needed) and knowledge of the app's webhook endpoint path (typically fixed/shared across all shops per the documented single-path registration pattern). No secrets, tokens, or victim credentials are needed — only the ability to send an HTTP request with modified headers, satisfying the "unprivileged internet user" scope.

### Recommendation
Bind the identity fields into the signed content check, not just the raw body:
- Reject webhooks where the `shopify-shop-domain` header does not correspond to a shop the receiving app instance actually expects/has an active registration for, independent of body HMAC validity.
- Where feasible, have `HmacValidator`/`Request` incorporate `shop` (and ideally `topic`) into what is cryptographically verified, or document explicitly (and enforce in `Registry.process`) that host apps MUST independently validate `data.shop` against their own known/installed shop list before trusting it, since HMAC only proves body integrity, not header authenticity.
- Add unit/fuzz tests asserting that mismatched header values (shop/topic changed, body/hmac unchanged) are rejected by `Registry.process`.

### Proof of Concept
```ruby
# Attacker installs the target app on their own store "attacker.myshopify.com"
# and receives a real webhook with a valid HMAC over the raw body.
raw_body = '{"id": 1, "note": "hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), app_secret_captured_from_own_legit_delivery, raw_body)
# (attacker never sees app_secret_key directly — it is the actual signature Shopify sent them)

# Attacker replays it to the app's shared webhook endpoint, swapping only the shop header:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),   # unchanged, still valid for raw_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate passes (body+hmac match)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_controlled_body, ...))
```
The handler receives attacker-controlled `body` attributed to `victim-shop.myshopify.com`, demonstrating the identity-binding break.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```
