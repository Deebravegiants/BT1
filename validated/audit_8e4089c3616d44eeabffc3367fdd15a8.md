### Title
Webhook `shop` domain is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `ShopifyAPI::Webhooks::Registry.process` accepts the webhook as authentic once that body-only HMAC validates. The `shop` field (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is never part of the signed material, yet it is passed straight into `WebhookMetadata` and handed to the app's handler as the trusted tenant identifier. Since the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app, any unprivileged user who installs the app on their own store can capture a genuinely-signed `(body, hmac)` pair and replay it to the app's webhook endpoint with a forged `shop` header pointing at a victim shop, producing a webhook the app will process as authentic and cross-tenant.

### Finding Description
The binding that should hold is:

`shop value verified by HMAC == shop value the handler acts on`

In this gem that binding does not exist:

- `HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it against the `hmac` field: [1](#0-0) 
- For webhooks, `to_signable_string` returns only `@raw_body`, and `shop` is read from an unauthenticated header, entirely independent of the signed bytes: [2](#0-1) 
- `Registry.process` validates only this body-only HMAC, then immediately forwards `request.shop` to the handler as the trusted tenant identifier: [3](#0-2) 
- `WebhookMetadata.shop` is a plain `String` const with no verification step, and the gem's own docs instruct developers to key business logic on `data.shop` directly (e.g. `shop_domain: data.shop`) as if it were verified: [4](#0-3) [5](#0-4) 

**Before attack**: legitimate webhook for shop A → `raw_body_A`, `hmac = HMAC(secret, raw_body_A)`, `shop header = A`. Signature check binds only to `raw_body_A`.
**Attacker's request sequence**: attacker installs the app on their own store (an ordinary, unprivileged action requiring no leaked credentials), causing Shopify to send them a real signed webhook `(raw_body_A, hmac)` for topic X. They resend this exact `(raw_body_A, hmac)` to the app's webhook endpoint but replace the `shopify-shop-domain` header with victim shop `B`.
**After attack**: `HmacValidator.validate` still returns `true` (it never examined the shop header), so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "B", body: raw_body_A_parsed, ...)`. The equality the protocol needs — "the shop whose signature was verified" == "the shop the handler is told to act on" — is broken; the attacker fully controls the right-hand side while only needing legitimate access to the left-hand side for a *different* tenant.

This is analogous to the `AxelarAdapter.execute()` issue in the reference report: a shared, permissionless verification surface (there: `execute()` with attacker-controlled gas; here: a shared HMAC secret with a body-only signature) lets an unprivileged party decouple a value the protocol/gem treats as atomic-with-verification (there: paired approve/issue messages; here: the `shop` claim vs. the signed body) from what was actually authenticated.

### Impact Explanation
Cross-tenant access: The app will invoke tenant-scoped business logic (order creation, data sync, session/token lookups keyed by `shop`, background jobs enqueued with `shop_domain: data.shop` as shown in the gem's own docs example) attributing an attacker-crafted event to a shop the attacker does not control and never authenticated against. Depending on how the host app uses `data.shop` (e.g., to look up that shop's stored access token/session and perform actions, or to write records into that shop's tenant data), this can lead to unauthorized cross-tenant data manipulation or triggering of privileged per-shop workflows using attacker-supplied body content. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
High likelihood of exploitability given the primitives involved:
- The attacker needs no privileged credentials, no access token, and no knowledge of `api_secret_key`: they simply install the (public) app on any shop they control — a normal, unprivileged onboarding flow.
- They then capture the (body, hmac) pair Shopify legitimately sends to their own callback endpoint and replay it with only the `shop` header altered; no cryptographic material needs to be forged since the signature never covered that header.
- The vulnerability is not a misuse of an undocumented API — the gem's own documented usage pattern (`webhooks.md`, `WebhookMetadata`) treats `data.shop` as if `Registry.process`'s successful HMAC check already vouches for it, actively encouraging developers to trust it directly.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the value that is actually verified, e.g.:
- Include the `shop` (and `webhook_id`/`topic`) in the signable string, or
- Require the host application to separately confirm that `request.shop` matches a shop for which the app holds an active session/webhook subscription before trusting it, and document this requirement explicitly rather than presenting `data.shop` as already-verified in `webhooks.md`.
- At minimum, update `ShopifyAPI::Webhooks::Registry.process` to cross-check the incoming `shop` header against the set of shops that currently have this webhook topic registered (already known to the app via `Registry`), rejecting requests for shops without an active registration for that topic.

### Proof of Concept
1. Attacker installs the target (public) app on `attacker-shop.myshopify.com` and registers for `orders/create` webhooks via the app's normal onboarding flow.
2. Shopify sends a legitimately signed webhook to the app's endpoint:
   ```
   POST /callback/orders/create
   shopify-topic: orders/create
   shopify-shop-domain: attacker-shop.myshopify.com
   shopify-hmac-sha256: <valid HMAC over raw_body>
   Body: raw_body (JSON order payload, attacker fully controls the order content on their own store)
   ```
3. Attacker replays the exact same request to the same endpoint, changing only the header:
   ```
   shopify-shop-domain: victim-shop.myshopify.com
   ```
   (`shopify-hmac-sha256` and body left untouched.)
4. Server-side, using this gem:
   ```ruby
   request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers_with_victim_shop)
   ShopifyAPI::Webhooks::Registry.process(request)
   ```
   `Utils::HmacValidator.validate(request)` returns `true` because it only re-hashes `raw_body`; `Registry.process` calls the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, i.e., the handler executes attacker-controlled data attributed to a shop the attacker never authenticated as.

Note: I was unable to inspect how downstream consumers of this gem (e.g., `shopify_app`) additionally cross-check `data.shop`, since that logic lives outside this repository's index; the finding is scoped strictly to `shopify_api`'s own `Webhooks::Request`/`Registry` verification contract, which does not bind `shop` to the HMAC.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** docs/usage/webhooks.md (L10-30)
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
```
