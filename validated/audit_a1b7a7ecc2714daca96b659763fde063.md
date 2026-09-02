This confirms the finding. The documentation explicitly states `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" [1](#0-0) , and the `data.shop` field passed to the handler is presented as a trusted identifier of "The shop domain of the webhook" [2](#0-1) , yet the shop domain header is never part of the signed payload.

### Title
Webhook shop-domain identity spoofing via unsigned header allows cross-tenant event forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [3](#0-2) 

`HmacValidator.validate` computes the HMAC exclusively over that signable string: [4](#0-3) 

The `shop` accessor, however, is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to the body or the HMAC: [5](#0-4) 

`Registry.process` only gates on the HMAC check and then forwards `request.shop` verbatim to the app's handler as if it were an authenticated attribute of the verified request: [6](#0-5) 

The equality the gem implicitly claims to hold is:
`shop_that_signed_this_body (cryptographically authenticated) == request.shop (header value delivered to the handler)`

In reality only `hmac(secret, raw_body) == received_hmac` is verified; the header is fully attacker-controlled and independent of the signed content. The gem's own documentation reinforces the false binding by describing `process` as verifying "the request did indeed come from Shopify" and describing `data.shop` as "The shop domain of the webhook" without qualification [1](#0-0) [2](#0-1) .

An unprivileged internet user who owns any shop (e.g., a free development/trial store using the same app) can:
1. Install the victim app on their own shop and let Shopify deliver one legitimate webhook (any topic) to the app's public callback endpoint, capturing the raw body and its valid `x-shopify-hmac-sha256` value.
2. Replay that exact `raw_body` + `hmac` pair directly to the same public callback URL, but with the `x-shopify-shop-domain` header rewritten to the victim merchant's domain.
3. `HmacValidator.validate` still succeeds (it only checks body+secret), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own body>, ...)`.

Because the webhook endpoint is a public, unauthenticated HTTP endpoint by design (Shopify must be able to call it from the internet), nothing on the wire prevents the attacker from making this second call themselves — no source-IP allowlisting, mTLS, or additional binding is enforced by this gem.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to establish between shops: the app is led to believe attacker-controlled body content originated from and pertains to the victim's shop. Depending on how the host app uses `data.shop` (which the gem explicitly recommends using as the shop key, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` in the documented example [7](#0-6) ), this can lead to cross-tenant data corruption/injection, forged mandatory-compliance events (`shop/redact`, `customers/redact`, `customers/data_request`) being attributed to the wrong merchant, or other cross-tenant state changes — a Critical-class cross-tenant access impact achieved purely by an unprivileged internet user replaying HTTP requests they can freely construct.

### Likelihood Explanation
Any user who can install the app once on a shop they control (including free/development stores) obtains a valid `(raw_body, hmac)` pair. Replaying it with a modified header requires no secret knowledge, no privileged access, and no TLS interception — only a normal HTTP client. Likelihood is high wherever a host app trusts `data.shop` from `Registry.process` as an authenticated tenant identifier, which is exactly the pattern the gem's own documentation recommends.

### Recommendation
Bind the shop identity to the verified content: either (a) include the `shop-domain` (and `topic`, `webhook-id`) header values in the HMAC-signed material construction expected by verification (not possible unilaterally since Shopify signs body only — so instead), or (b) require host applications to cross-check `request.shop` against a shop for which the app holds an active, previously-issued access token/session before trusting the webhook as belonging to that shop, and clearly document that `shop`/`topic`/`webhook_id` headers are **not** covered by the HMAC and must not be treated as authenticated on their own. Consider exposing a stricter `Registry.process` mode that only accepts webhooks for shops with a known active installation.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a free/dev store) and registers any webhook topic.
2. Shopify delivers `POST /callback/<topic>` to the app with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `B` and `H` (they own the delivery, no interception needed).
4. Attacker sends their own `POST /callback/<topic>` request to the app's public endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (body/secret match), so `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled B>, ...)`, even though the victim shop never sent this event.

### Citations

**File:** docs/usage/webhooks.md (L14-14)
```markdown
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
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
