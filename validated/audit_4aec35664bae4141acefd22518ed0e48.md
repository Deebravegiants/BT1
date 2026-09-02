The docs explicitly document `shop` as coming from the webhook, and the gem's own `Registry.process` claims to "verify the request did indeed come from Shopify" — but the verification (`Utils::HmacValidator.validate`) only authenticates the raw body bytes, not the shop domain. This confirms the finding rather than excluding it: the gem itself, not just a host app choice, feeds an unauthenticated `shop` value into the handler while claiming the request has been verified.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the HMAC [2](#0-1) . `Utils::HmacValidator.validate` computes and compares the HMAC solely against `to_signable_string` (i.e., the body) [3](#0-2) , so an HMAC that validates says nothing about which shop the webhook is "from." `Registry.process` nonetheless treats a passing HMAC check as proof the request "did indeed come from Shopify" for the claimed shop and forwards `request.shop` unchanged into the app-level handler [4](#0-3) , and the docs instruct integrators to trust `data.shop` as "The shop domain of the webhook" [5](#0-4) .

### Finding Description
The `client_secret`/`api_secret_key` used to sign webhooks is a single, app-wide secret shared across every shop that installs the app — it is not shop-specific [6](#0-5) . Because the HMAC is computed over the body only, any two webhook deliveries carrying byte-identical bodies (e.g., a genuine webhook the attacker legitimately received for their own shop, or a webhook whose body is attacker-controlled/predictable such as `orders/create` payloads with attacker-supplied field values) share the exact same valid `hmac` regardless of which shop the header claims. The identity binding the code implicitly relies on is:

`HMAC_valid(body, secret) == true` ⇒ `shop header == true origin shop`

but the actual guarantee provided by the code is only:

`HMAC_valid(body, secret) == true` ⇒ `body was produced by holder of secret` (which is Shopify for legitimate merchants, but the resulting message is shop-agnostic).

An attacker who owns/controls their own Shopify store with the app installed receives legitimately-signed webhooks for that store. Because `shop-domain` is not part of the signed content, the attacker can replay the identical `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header value naming a victim shop. `Utils::HmacValidator.validate` still returns `true` since it never inspects the shop header [7](#0-6) , `Registry.process` proceeds to dispatch to the topic handler with `shop: request.shop` set to the attacker-chosen victim domain [4](#0-3) .

### Impact Explanation
Because `WebhookMetadata.shop` is the tenant key that host applications are documented to use for looking up per-shop state (sessions, access tokens, local records) [8](#0-7) , an attacker-controlled shop value routed through a "verified" webhook enables cross-tenant actions: injecting fabricated events attributed to a victim shop (e.g., triggering app business logic — data deletion, order processing, GDPR-style compliance webhook handling, entitlement changes — keyed on the attacker's chosen victim shop domain) without ever needing that victim's credentials. This satisfies the Critical bar of cross-tenant access, since the gem's own verification primitive is what mis-attributes trust.

### Likelihood Explanation
Any unprivileged internet user can freely create a Shopify development/partner store and install a public app there, giving them a stream of genuinely-signed webhooks (valid `raw_body`/`hmac` pairs) for that store. Sending these to the target app's public webhook callback URL with a forged shop header requires only basic HTTP tooling — no secret, token, or elevated access is needed to alter unsigned headers.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`/`api_version`) in the value that is HMAC-verified, or otherwise cryptographically/positively bind the claimed shop to the signed payload before it is passed to handlers — e.g., verify the `shop` domain against the app's registered/known shops for that webhook delivery, or require the caller to separately authenticate the shop before trusting `data.shop`. At minimum, `Registry.process`/`Utils::HmacValidator` should not be documented or treated as proof that the whole webhook envelope (including shop) "did indeed come from Shopify" for the claimed tenant.

### Proof of Concept
1. Attacker registers a Shopify partner/dev store `attacker.myshopify.com`, installs the target app, and triggers a webhook (e.g. `orders/create`) which Shopify signs and delivers to the app: headers include `X-Shopify-Hmac-Sha256: <hmac>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Topic: orders/create`, and body `B`.
2. Attacker captures `(B, hmac)`.
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `hmac`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `hmac` returns the unchanged decoded value [9](#0-8) ; `to_signable_string` returns `B` [1](#0-0) .
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares it to the attacker-supplied (originally-legitimate) `hmac` — it matches, since the secret and body are unchanged [3](#0-2) .
6. The handler is invoked with `WebhookMetadata.shop == "victim.myshopify.com"` [10](#0-9) , even though the event never originated from that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
