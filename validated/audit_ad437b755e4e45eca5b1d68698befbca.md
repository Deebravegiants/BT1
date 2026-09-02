### Title
Webhook `shop-domain` and `topic` headers are trusted for tenant routing while the HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate(request)` authenticates the body bytes only [2](#0-1) . The `shop` and `topic` values that `Registry.process` uses to route and attribute the webhook are read straight from unauthenticated HTTP headers (`shopify-shop-domain`, `shopify-topic`) [3](#0-2) , and are never covered by the signature.

### Finding Description
The identity binding that should hold is:

`hmac(raw_body, client_secret) valid` ⇒ `(shop, topic, body)` are all authentic and bound together

but in this gem the binding actually enforced is only:

`hmac(raw_body, client_secret) valid` ⇒ `raw_body` is authentic

`Registry.process` verifies the HMAC and then immediately trusts the caller-supplied `shop` and `topic` headers to build `WebhookMetadata` and dispatch the corresponding handler: [4](#0-3) 

Since `to_signable_string` only returns the raw body [1](#0-0) , an unprivileged internet user who obtains any single valid `(raw_body, hmac)` pair — e.g. from a legitimate webhook that Shopify already delivered for their own shop, since every merchant/app-installer can see their own webhook deliveries — can replay that exact body+hmac to the app's public webhook endpoint while freely rewriting the `X-Shopify-Shop-Domain` and `X-Shopify-Topic` headers to any value. `HmacValidator.validate` still returns `true` because those headers are outside the signed data, and `Registry.process` will happily route the (attacker-chosen) topic to the registered handler and hand it an attacker-chosen `shop` in `WebhookMetadata#shop` [5](#0-4) .

Host applications (per this gem's own documented pattern) key sessions and per-tenant state by the `shop` value coming out of authenticated Shopify inputs (OAuth callback, JWT `dest`, etc. — see `Auth::JwtPayload#shop` and `SessionUtils.offline_session_id` [6](#0-5) ). The webhook path breaks this convention: the tenant identifier fed to the handler is not bound to the cryptographic signature at all, unlike every other authenticated-input path in this library (OAuth `AuthQuery`, whose `shop`, `code`, `state`, `host`, `timestamp` are all part of `to_signable_string` [7](#0-6) ).

### Impact Explanation
This is a cross-tenant impact: a party who legitimately controls one Shopify shop with the app installed can forge webhook deliveries that the host application attributes to any other shop and any topic, because `Registry.process`/`WebhookMetadata` treat the unauthenticated `shop`/`topic` headers as trustworthy tenant identity once the (unrelated) body HMAC check passes [8](#0-7) . Depending on how the host app's handler uses `data.shop`/`data.topic` (e.g., updating per-shop state, deleting data for `shop/redact`/`customers/redact`, disabling features on `app/uninstalled`), this enables cross-tenant data manipulation using only a replayed body/hmac pair the attacker legitimately received for their own shop.

### Likelihood Explanation
Medium-to-High: the attacker needs no secret material — only one previously observed valid `(raw_body, hmac)` pair, which any shop owner with the app installed will naturally have from their own normal webhook traffic. No `api_secret_key`, access token, or privileged account access to the target shop is required, only network access to POST to the app's public webhook endpoint with custom headers.

### Recommendation
Bind the `shop` and `topic` (and ideally `webhook_id`/`api_version`) header values into the signed material that `HmacValidator` verifies, or otherwise cryptographically bind them to the raw body before trusting them for routing (e.g., derive/verify them from a separately Shopify-signed value, or require the host app to compare the header-derived shop against an out-of-band-known shop for that specific webhook subscription). At minimum, `Webhooks::Request#to_signable_string` should not treat `shop`/`topic` as implicitly authenticated once `hmac` validates only the body.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. topic `orders/create`, with raw body `B` and Shopify-computed header `X-Shopify-Hmac-Sha256: H` (valid for `HMAC(client_secret, B) = H`).
2. Attacker sends a new HTTP POST to the app's public webhook endpoint with:
   - Body: the same bytes `B`
   - Header `X-Shopify-Hmac-Sha256: H` (unchanged)
   - Header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (changed)
   - Header `X-Shopify-Topic: shop/redact` or any registered topic (changed)
3. `ShopifyAPI::Webhooks::Request.new` parses these headers [9](#0-8) ; `Utils::HmacValidator.validate(request)` succeeds because it only re-hashes `raw_body` [10](#0-9) [1](#0-0) .
4. `Registry.process` dispatches the registered handler for the attacker-chosen topic with `shop: "victim-shop.myshopify.com"` in `WebhookMetadata` [4](#0-3) , causing the host app to act on the victim shop's tenant data using a webhook the victim never actually received.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
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

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/session_utils.rb (L58-66)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
