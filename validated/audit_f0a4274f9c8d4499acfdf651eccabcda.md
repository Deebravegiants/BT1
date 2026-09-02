## Answer

The reported issue is real and reproducible in this gem's own code, though it is worth noting up front that it mirrors Shopify's documented HMAC scheme (body-only signing) rather than being a novel implementation bug — the flaw is that this gem then treats the unsigned header values as if they were authenticated when it hands them to the webhook handler.

### Title
Webhook shop/topic/api-version/webhook-id headers are trusted as authenticated despite being outside HMAC coverage - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates nothing but the JSON body [1](#0-0) . `Registry.process` nonetheless calls `HmacValidator.validate(request)` and, on success, forwards `request.topic`, `request.shop`, `request.api_version`, and `request.webhook_id` straight to the handler as though they were verified [2](#0-1) , even though these values come from headers that `initialize` never requires (`api-version`/`webhook-id` are optional) and are never fed into the signature.

### Finding Description
The broken binding is: `HMAC-valid(raw_body) == authenticated(shop, topic, api_version, webhook_id)`. This does not hold. `initialize` only requires `topic`, `hmac-sha256`, and `shop-domain` headers to be *present* (not that they match anything signed) [3](#0-2) , and `api-version`/`webhook-id` are entirely optional at construction time yet `T.cast` to `String` at the accessor [4](#0-3) . `to_signable_string` — the only input to `HmacValidator.validate_signature` — is just `@raw_body` [1](#0-0) [5](#0-4) . Because the app's `api_secret_key` is shared across every shop that installs it, an attacker who legitimately installs the app on their own development shop can capture a genuinely-signed `(raw_body, hmac)` pair for their own webhook, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting `x-shopify-shop-domain` (and/or `x-shopify-api-version`, `x-shopify-webhook-id`) for a victim shop's domain. `HmacValidator.validate` still passes because it only checks `raw_body` against the secret [6](#0-5) , and `Registry.process` then calls the handler with `shop: request.shop` set to the attacker-chosen value [7](#0-6) . No `ShopValidator.sanitize!` or equivalent check is applied to `request.shop` anywhere in `Registry` or `Request` — that validator exists in the codebase (`lib/shopify_api/utils/shop_validator.rb`) but is only used in OAuth/token-exchange flows, not in the webhook path [8](#0-7) .

### Impact Explanation
Any code that trusts `WebhookMetadata#shop`/`#topic`/`#api_version`/`#webhook_id` as "this came from Shopify for this shop" (a reasonable assumption given the gem's naming and the fact that `Registry.process` gates on `HmacValidator.validate` first) can be made to act on data tagged with an arbitrary victim shop domain, using a body the attacker fully controls (via their own legitimate installation). This is a cross-tenant authentication-bypass class issue: the attacker never needs `api_secret_key`, only a genuine webhook of their own.

### Likelihood Explanation
This requires: (1) the target app uses a single shared `api_secret_key` across shops — true for any standard public app, which is the default and documented configuration; (2) the attacker installs the app on their own store and subscribes to at least one webhook topic — both self-service and free; (3) the handler uses `data.shop`/`data.topic` from `WebhookMetadata` to key data operations rather than independently verifying shop identity — a very common pattern since the gem's own architecture implies these fields are validated once `HmacValidator.validate` passes. Cost to the attacker is a single dev-store signup and a replayed HTTP POST; it is fully repeatable against any shop domain string of the attacker's choosing.

### Recommendation
Document (and/or enforce) that `request.shop`, `request.topic`, `request.api_version`, and `request.webhook_id` are **not** cryptographically authenticated by `HmacValidator.validate` — only `raw_body` is. `Registry.process` should require callers to cross-check `request.shop` against a known/installed shop record (e.g., via `ShopValidator.sanitize!` plus a session/store lookup) before trusting it for any tenant-scoped action, and this expectation should be made explicit in `docs/usage/webhooks.md`.

### Proof of Concept
```ruby
# test/webhooks/registry_test.rb (new test)
def test_shop_header_is_not_covered_by_hmac
  body = "{}"
  hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, body)
  encoded_hmac = Base64.encode64(hmac)

  received_shops = []
  handler = TestHelpers::FakeWebhookHandler.new(->(data) { received_shops << data.shop })
  ShopifyAPI::Webhooks::Registry.add_registration(topic: "orders/create", path: "path",
    delivery_method: :http, handler: handler)

  ["shop-a.myshopify.com", "shop-b.myshopify.com"].each do |shop|
    headers = {
      "x-shopify-topic" => "orders/create",
      "x-shopify-hmac-sha256" => encoded_hmac,
      "x-shopify-shop-domain" => shop,
    }
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)
    )
  end

  # Same body + same HMAC, but two different "authenticated" shops were accepted
  assert_equal(["shop-a.myshopify.com", "shop-b.myshopify.com"], received_shops)
end
```
This asserts both sides of the claimed binding directly: identical `(raw_body, hmac)` passes `HmacValidator.validate` for two different `shop` values, proving `shop` is not bound to the signature.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L25-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L50-59)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
