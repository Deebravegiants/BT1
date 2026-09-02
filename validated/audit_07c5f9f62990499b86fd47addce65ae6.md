### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing on otherwise valid webhook deliveries - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` attribute solely from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body, not this header. `Registry.process` trusts this unauthenticated header value and passes it straight into the merchant-facing `WebhookMetadata#shop` field delivered to the app's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively over that signable string [2](#0-1) . Meanwhile `Request#shop` is read directly from the `shop-domain` header with no cross-check against the signed payload [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` object handed to the app's own `WebhookHandler#handle` implementation: [4](#0-3) . This breaks the identity binding `hmac(raw_body) == hmac_covers(shop)`: the byte range that is cryptographically verified (`raw_body`) is not the same as the field the library treats as the authenticated tenant identifier (`shop-domain` header).

This is the same bug class as the referenced report — a value the code relies on for identity/behavior (`from`/collateral owner in the analog; `shop` here) is not the value actually protected by the security check (transferFrom target in the analog; HMAC-signed bytes here).

By contrast, the OAuth callback path in this gem does this correctly: `AuthQuery#to_signable_string` explicitly includes `shop` in the signed parameter set [5](#0-4) , so shop-spoofing is not possible there. The webhook path lacks this equivalent binding.

### Impact Explanation
Because `shop` is not part of the signed content, any party who can replay or relay a legitimately-signed webhook body (e.g., a proxy, a component that forwards webhook payloads, or anyone who can influence headers reaching the app's webhook endpoint while preserving body+HMAC) can cause the app to process the payload under an attacker-chosen `shop` value instead of the true originating shop. Because `WebhookHandler` implementations key their side effects (data storage, entitlement changes, uninstall handling, etc.) off `WebhookMetadata#shop`, this can lead to cross-tenant data being attributed to the wrong merchant, meeting the "cross-tenant access" bar for a valid finding.

### Likelihood Explanation
The library's own header-normalization logic already treats `shopify-*` and `x-shopify-*` header variants interchangeably and does no additional binding checks [6](#0-5) , so no additional gem-level protection exists against header tampering. Exploitability, however, depends on the host application's HTTP stack/infrastructure permitting header injection or on any intermediary/relay in the delivery path — which is outside this gem's control. Within the gem's own logic, the missing binding is unambiguous and directly demonstrable: the same HMAC validates for any `shop` header value paired with the same body.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed material, or otherwise cryptographically bind the header-derived `shop` to the payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document that `Request#shop` is unauthenticated and that host applications must independently verify the shop domain (e.g., against their own installed-shops list) before acting on webhook data.

### Proof of Concept
```ruby
raw_body = "{}"
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), ShopifyAPI::Context.api_secret_key, raw_body)

# Attacker-controlled shop header, same body+hmac as a legitimate webhook for "victim-shop.myshopify.com"
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com", # forged, not covered by HMAC
}

req = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(req)
# => HmacValidator.validate(req) succeeds because it only checks raw_body,
#    and the handler receives WebhookMetadata(shop: "attacker-shop.myshopify.com")
#    even though the signature was for a payload delivered under a different shop context.
``` [4](#0-3) [7](#0-6)

### Citations

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
