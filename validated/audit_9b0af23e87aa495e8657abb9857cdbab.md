### Title
Webhook `shop`/`topic` identity not bound to HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` as plain header reads, but `to_signable_string` — the value actually protected by the HMAC signature — is only the raw request body. [1](#0-0)  `Utils::HmacValidator.validate` only proves that the body was signed with `Context.api_secret_key`; it says nothing about which shop or topic that signed body belongs to. [2](#0-1)  `Webhooks::Registry.process` nonetheless treats a passing HMAC check as authorization to dispatch the handler using the unauthenticated `shop` header. [3](#0-2) 

### Finding Description
The binding that should hold is:

`HMAC_valid(body) == true` should imply `request.shop == the tenant that Shopify actually generated this exact (body, hmac) pair for`.

In this gem that equality does not hold, because the HMAC signature covers only `@raw_body` and not the `shop-domain`/`topic` headers [4](#0-3) . Since `api_secret_key` is the *same shared secret* for every shop that installs a given (public) app, any unprivileged internet user can:

1. Install the target app on their own Shopify dev/trial store (no special privilege required for a publicly listed app).
2. Receive a legitimate webhook delivery from Shopify for their own store — this webhook has a body they fully control (e.g. by editing an order, updating shop settings, or uninstalling the app) and a **valid** `X-Shopify-Hmac-Sha256` computed with the real `api_secret_key`.
3. Replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain.

`Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because the body/hmac pair is genuinely valid [5](#0-4) . It then builds `WebhookMetadata` using `request.shop` (the attacker-supplied header) and dispatches it to the app's handler as if it came from the victim tenant [6](#0-5) . This is a direct analog of the report's class: a field acted on downstream (`shop`) that is not covered by the same integrity check (`hmac`) that is otherwise trusted to authenticate the request.

### Impact Explanation
This breaks the tenant isolation the whole webhook subsystem is supposed to provide: any handler logic keyed off `WebhookMetadata#shop` (billing state changes, data deletion on `app/uninstalled`, order/inventory sync, GDPR mandatory webhooks, etc.) can be triggered for a shop the attacker does not own, using data the attacker fully controls. That constitutes cross-tenant access/action — the app cannot distinguish "genuine event for shop Y" from "attacker's own event replayed and relabeled as shop Y" — which meets the Critical bar (cross-tenant access) defined in scope.

### Likelihood Explanation
High. The attack requires none of the excluded prerequisites (`api_secret_key`, an access token, TLS interception, privileged account, local access, or social engineering). It only requires: (a) the ability to install a publicly available app on an attacker-controlled shop — a normal unprivileged action — and (b) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is trivial for any internet user since that endpoint must be internet-reachable to accept Shopify's webhook deliveries in the first place.

### Recommendation
Bind the shop (and ideally topic) identity into the value that is actually verified, e.g. by having `HmacValidator`/`Request#to_signable_string` incorporate the `shop-domain` header (and other identity-bearing headers) into the signed material, or by requiring the caller (host application) to independently verify that `request.shop` corresponds to a shop it has an active installation/session for before trusting the payload. At minimum, document prominently that `Registry.process`'s HMAC check only authenticates the body and that consuming applications must not treat `WebhookMetadata#shop`/`#topic` as authenticated unless they perform their own additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook they subscribed to (e.g. `orders/create`) with a body of their choosing (order fields are attacker-controlled on their own store). Shopify sends:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw body, computed with the app's shared api_secret_key>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {...attacker-controlled JSON...}
   ```
3. Attacker captures this exact `(raw_body, X-Shopify-Hmac-Sha256)` pair.
4. Attacker sends a new POST directly to the app's public webhook endpoint:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same valid HMAC as captured>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: <same attacker-controlled JSON>
   ```
5. `ShopifyAPI::Webhooks::Request.new` parses this successfully [7](#0-6) , `Utils::HmacValidator.validate` returns `true` because the body/hmac pair is genuinely valid [8](#0-7) , and `Registry.process` invokes the app's `orders/create` handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body` [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
