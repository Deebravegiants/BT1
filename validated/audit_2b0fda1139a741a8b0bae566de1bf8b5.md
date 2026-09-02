### Title
Webhook HMAC only signs the raw body, not the `shop-domain` or `topic` headers, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` for webhook HMAC verification, but its `to_signable_string` returns only the raw request body. The `shop`, `topic`, `api_version`, and `webhook_id` values that `Registry.process` uses to select a handler and to attribute the payload to a specific shop are read straight from HTTP headers that are never part of the HMAC-signed material. This breaks the identity binding `HMAC-authenticated bytes == bytes acted upon`: the signature authenticates the body only, while dispatch and shop attribution are driven by unauthenticated header values.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [1](#0-0) 

`Request#shop` and `Request#topic` are read from headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Registry.process` verifies the HMAC, then dispatches purely on `request.topic` and forwards `request.shop` as the tenant identifier to the handler, without re-checking that these header values are consistent with anything cryptographically bound to the signed body: [3](#0-2) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string` (i.e., the raw body) and the app's `api_secret_key`, which is a single shared secret for the whole app across every shop that installs it: [4](#0-3) 

Because the secret is shared across all shops of the app (not shop-specific), and because `shop`/`topic` headers are excluded from the signed material, any party who can obtain one valid `(raw_body, hmac)` pair for the app — trivially, by installing the app on their own shop and receiving a real webhook — can resend that exact body/HMAC to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain` (or `X-Shopify-Topic`) header. `Utils::HmacValidator.validate(request)` will still return `true` because the signature check only covers the body bytes, and `Registry.process` will happily hand the payload to the handler labeled with the attacker-chosen `shop`/`topic`.

Equality that should hold but doesn't: `shop attributed by handler == shop cryptographically bound by the HMAC`. In this implementation, the HMAC binds nothing about shop identity — the "identity" of the request is entirely attacker-supplied metadata.

### Impact Explanation
This is a cross-tenant integrity violation: an attacker (an unprivileged party who merely installs the app on their own shop, which is a normal, uncredentialed action many public apps allow) can inject payloads that the app processes as if they originated from a victim shop, because the `shop` header carrying the tenant identity is not covered by the signature. Depending on how the host application's `WebhookHandler` implementation trusts `WebhookMetadata#shop`, this can lead to writing/reading data under a spoofed tenant, i.e., cross-tenant access — one of the explicitly listed Critical impacts.

### Likelihood Explanation
Likelihood is bounded by the fact that obtaining a valid `(body, hmac)` pair requires actually receiving a webhook (e.g., by installing the target app on an attacker-controlled shop), which is a low but nonzero barrier for any public app. Once obtained, replay against the same endpoint with forged headers is trivial (no secret material needed) since the HMAC is exclusively body-bound.

### Recommendation
Include the shop domain and topic (and any other headers the handler trusts) as part of the signed material verified against the request, or independently authenticate/authorize the `shop` claim before dispatching (e.g., by validating it against a known-installed shop record before invoking the handler), rather than trusting `X-Shopify-Shop-Domain` verbatim once only the body HMAC has passed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a legitimate webhook (e.g., `orders/create`) and captures the raw POST body and its `X-Shopify-Hmac-Sha256` header value — both signed using the app's single, shop-agnostic `api_secret_key`. [5](#0-4) 
3. Attacker resends this exact `(raw_body, hmac)` to the app's webhook endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim.myshopify.com` and/or changes `X-Shopify-Topic`. [6](#0-5) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body bytes against the HMAC. [7](#0-6) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload actually came from the attacker's own shop, and processes/stores it as victim-shop data.

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
