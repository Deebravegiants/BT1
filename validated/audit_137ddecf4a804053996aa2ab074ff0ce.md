### Title
`Webhooks::Request#shop`/`#topic` are read from unsigned headers while `HmacValidator` only authenticates `@raw_body` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `HmacValidator.validate` recomputes and compares the HMAC over the body alone [2](#0-1) . The `topic`, `shop`, `api_version`, and `webhook_id` values are pulled straight from attacker-controlled HTTP headers via `shopify_header` [3](#0-2) [4](#0-3) , and none of them are re-checked against the signature. Because `Context.api_secret_key` is a single, app-wide secret shared across every shop that installs the app (not per-shop) [5](#0-4) , any attacker who can obtain one validly-signed webhook body (e.g., by installing the app on their own development shop and receiving their own webhook) can replay that exact `raw_body` + HMAC to the app's public webhook endpoint while forging the `x-shopify-shop-domain` and/or `x-shopify-topic` headers to name an arbitrary victim shop or a different topic (including mandatory GDPR topics like `customers/redact`).

### Finding Description
The broken binding is: **`HmacValidator.validate(request) == true` should imply `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` were also authenticated by Shopify for this exact delivery.** In this code that equality does not hold, because `validate_signature` only recomputes the digest over `verifiable_query.to_signable_string`, which for `Webhooks::Request` is just `@raw_body` [1](#0-0) [6](#0-5) .

`Request#initialize` only verifies presence of the `shopify-topic`/`x-shopify-topic`, `shopify-hmac-sha256`/`x-shopify-hmac-sha256`, and `shopify-shop-domain`/`x-shopify-shop-domain` header pairs — it never checks that the two forms agree when both are present, and it performs no binding of these values into the signature [7](#0-6) . `shopify_header` then resolves the value with `@headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]`, so whichever prefix is present (or preferred by precedence when both are present) wins, with no signature coverage of that choice [4](#0-3) .

Downstream, `Registry.process` uses this unauthenticated `request.topic` to select the handler from the registry and builds `WebhookMetadata` from the unauthenticated `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id`, handing all of it to the app's handler as if it were verified [8](#0-7) .

Exploit flow:
1. Attacker creates a development shop, installs the target app, and receives a legitimately signed webhook for their own shop — capturing `raw_body` and its correct `X-Shopify-Hmac-Sha256`.
2. Attacker POSTs the identical `raw_body` and HMAC header to the app's webhook endpoint again, but sets `x-shopify-shop-domain` to a victim shop's domain (or sets `x-shopify-topic` to a sensitive topic such as `customers/redact`).
3. `HmacValidator.validate` recomputes the HMAC over `raw_body` only, using the single app-wide `api_secret_key`, and it matches — validation succeeds even though the shop/topic were altered.
4. `Registry.process` dispatches to the handler for the forged topic and passes the forged shop identity, and the app's business logic acts on data it believes is authenticated for the victim shop/topic.

None of the existing guards stop this: `HmacValidator.validate` only checks `hmac` presence and the body signature [5](#0-4) ; there is no `ShopValidator.sanitize!` call anywhere in the webhook request/registry path; and Sorbet's `T.cast(shopify_header(...), String)` only enforces type, not authenticity.

### Impact Explanation
An attacker with no privileges beyond the ability to install the app on their own shop can cause the app to process a webhook event as if it originated from an arbitrary victim shop, or under an arbitrary (attacker-chosen) topic, using nothing but a replayed, previously-observed signed body. This is a cross-tenant identity confusion / authentication bypass: the app's handler logic trusts `WebhookMetadata#shop` and `#topic` as authenticated, when they are not bound to the signature at all. Depending on what the app does with mandatory topics (e.g., `customers/redact`, `shop/redact`) or shop-scoped writes keyed by `request.shop`, this can trigger unintended data deletion/mutation attributed to a shop that never sent the event, or misroute a webhook to the wrong handler. This is repeatable against any victim shop domain string the attacker chooses, for as long as the attacker retains one valid signed body/HMAC pair.

### Likelihood Explanation
Preconditions are minimal and attacker cost is low: register a development shop (Shopify permits this to any user), install the target app, capture one legitimate webhook delivery, and replay it with modified headers to the app's public webhook endpoint. No secret material, session, or elevated privilege is required. The only dependency is that the app's `api_secret_key` is shared across all shops (standard for non-custom apps), which is the normal Shopify app configuration.

### Recommendation
Bind the routing-critical header values into the signed material, or otherwise authenticate them independently of the raw body:
- Reject requests where both `shopify-<name>` and `x-shopify-<name>` are present but disagree, in `Request#initialize`.
- After HMAC validation, cross-check `request.shop` against the set of shops actually installed/known to the app (e.g., via `ShopValidator.sanitize!` plus a session/install lookup) before dispatching to a handler.
- Consider including topic/shop/webhook-id in the value passed to `HmacValidator` (or performing a secondary check) so that a captured signature for one shop/topic cannot be replayed under a different shop/topic.

### Proof of Concept
Minitest + WebMock/Mocha plan (`test/webhooks/registry_test.rb` style, no live shop):
1. `ShopifyAPI::Context.setup(api_secret_key: "secret", ...)`.
2. Build `raw_body = '{"id":1}'` and compute `hmac = OpenSSL::HMAC.digest("sha256", "secret", raw_body)` then Base64-encode it, matching `HmacValidator.compute_signature`.
3. Construct `request1 = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: {"x-shopify-hmac-sha256" => hmac_b64, "x-shopify-topic" => "orders/create", "x-shopify-shop-domain" => "attacker-shop.myshopify.com"})`.
4. Construct `request2` with the identical `raw_body`/`hmac` but `"x-shopify-shop-domain" => "victim-shop.myshopify.com"`.
5. Assert `ShopifyAPI::Utils::HmacValidator.validate(request1) == true` and `ShopifyAPI::Utils::HmacValidator.validate(request2) == true` — i.e., the same signature validates for two different shop identities.
6. Register a stub handler in `ShopifyAPI::Webhooks::Registry` for `orders/create`, call `Registry.process(request2)`, and assert the handler's `WebhookMetadata#shop` equals `"victim-shop.myshopify.com"` even though only `request1`'s shop was ever "legitimately" delivered — demonstrating one HMAC signature is accepted for two different tenant identities.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L46-63)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
