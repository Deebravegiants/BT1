### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, then hands `request.shop` straight to the app's handler as trusted data. The HMAC, however, is computed only over the raw body — never over the `X-Shopify-Shop-Domain` header. Since every shop that installs the same app shares the same `api_secret_key`, a valid `(raw_body, hmac)` pair captured from one legitimate installation remains valid when replayed with a forged `shop-domain` header claiming to be a different shop.

### Finding Description
`Request#to_signable_string` only returns the raw body: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all pulled straight from unauthenticated headers: [2](#0-1) 

`HmacValidator.validate` computes the signature only against `verifiable_query.to_signable_string` (i.e., the body), so it never binds the `shop` header to the signature: [3](#0-2) 

`Registry.process` performs exactly one check — HMAC over the body — and then forwards the unauthenticated `request.shop` value into `WebhookMetadata`, which is what the host app's handler uses to decide which tenant's data to act on: [4](#0-3) 

This breaks the intended identity binding `hmac == HMAC(secret, body || shop)`: the code only enforces `hmac == HMAC(secret, body)`, leaving `shop` (and the other Shopify headers) completely unauthenticated, i.e. `shop_verified != shop_used_by_handler`.

The documentation reinforces the false assumption that the whole request, including the shop identity, is verified: "This will verify the request did indeed come from Shopify and then call the specified handler," and the `shop` field is documented as simply "The shop domain of the webhook" with no caveat that it is unauthenticated. [5](#0-4) [6](#0-5) 

### Impact Explanation
An attacker who has a shop with the target app installed (an unprivileged, low-trust position — merely "a shop that installed the app") can trigger legitimate webhook deliveries to capture valid `(raw_body, hmac)` pairs signed with the app's shared `api_secret_key`. They can then replay that exact body/HMAC to the app's public webhook endpoint while spoofing `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) to any other merchant shop. `Registry.process` will accept it as authentic and invoke the handler with `data.shop` set to the victim shop, causing the host application to process attacker-controlled data as if it originated from a different tenant — a cross-tenant confusion/spoofing primitive that can lead to corrupting or triggering actions against another merchant's account within the app.

### Likelihood Explanation
Likelihood is Low/Medium in practice: the attacker needs (a) their own working installation of the target app to legitimately receive at least one webhook (freely obtainable for any public app), and (b) the ability to send arbitrary HTTP requests with custom headers to the app's public webhook endpoint (routine). No access to `api_secret_key`, access tokens, or any privileged account is required — only ordinary use of the app as any merchant.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise cryptographically tie the header values to the verified body, e.g.:
```ruby
def to_signable_string
  "#{shop}\n#{@raw_body}"
end
```
and update server-side verification accordingly (this requires coordinating with Shopify's signature scheme, since Shopify itself only signs the body — so at minimum the gem should document loudly, and ideally enforce via an opt-in check, that `data.shop` must be cross-checked by the host app against a known/authorized shop list before being trusted, rather than presenting it as already verified).

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" with the app installed and
# captures a real webhook delivery's raw body + HMAC from Shopify.
captured_raw_body = '{"id":1}'
captured_hmac = "<valid Shopify-computed HMAC for captured_raw_body>"

forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # spoofed
  "x-shopify-webhook-id" => "attacker-controlled-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Handler is invoked with data.shop == "victim-shop.myshopify.com",
#    even though the webhook never originated from that shop.
```

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L10-16)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
