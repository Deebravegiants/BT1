### Title
Webhook `shop` attribution is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` value used to attribute the webhook to a merchant tenant is read from an HTTP header that is never included in that signature. Because a single app-level `client_secret` is shared across every merchant that installs the app, anyone who legitimately receives one webhook for their own store can replay its body while swapping the `shop-domain` header to any other installed shop, and the signature will still validate.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` only proves that `to_signable_string` (i.e. the raw body bytes) matches the app's `api_secret_key`; it never checks `shop`: [4](#0-3) 

`Registry.process` trusts `request.shop` after only validating the HMAC, and forwards it as the tenant identifier to the app's webhook handler: [5](#0-4) 

This breaks the identity binding `shop_authenticated_by_hmac == shop_used_for_tenant_dispatch`. The HMAC only authenticates *that the body bytes were signed with the app's secret at some point*, not *which shop* they belong to. Since the `client_secret`/webhook signing secret is shared by the app across all of its installed shops (not shop-specific), any shop that has the app installed can:
1. Legitimately receive a real webhook for their own store (with a valid HMAC over the raw body).
2. Replay the exact same raw body to the app's webhook endpoint, but substitute the `shopify-shop-domain` header with a victim shop's domain (`victim.myshopify.com`, a publicly guessable/known value).
3. `HmacValidator.validate` still returns `true` because it only re-hashes `@raw_body`, which is unchanged.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` with the forged `shop`, causing the app's handler logic to act as if the payload came from the victim tenant.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an unprivileged party who merely installs the target app on their own (attacker-controlled) shop can cause the app to process/store/act on arbitrary body content while attributing it to a different, victim merchant. Depending on how the host application's webhook handlers use `shop` (e.g. updating per-shop data stores, triggering shop-scoped side effects, or deciding what to sync), this can lead to cross-tenant data corruption or disclosure — satisfying the "cross-tenant access" Critical impact category, achieved without ever needing the victim's access token or credentials.

### Likelihood Explanation
Likelihood is realistic: the attacker only needs to be able to install the app on any shop (a normal, unprivileged action for public apps) to obtain one genuine signed webhook body, and knowledge of a target `*.myshopify.com` domain (public information) to forge the header. No secrets, tokens, or elevated access are required — only the ability to send an HTTP request with a modified header to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the signed content, or otherwise verify these header values are consistent with a signed claim, before trusting them for tenant dispatch. Since Shopify's own signature only covers the body, the app-side fix should be to independently verify that the resolved `shop` corresponds to a shop with an active, known installation/session before dispatching to handlers, rather than trusting the raw header value implicitly once HMAC validation passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <valid-signature-over-raw-body>
   shopify-shop-domain: attacker-shop.myshopify.com
   shopify-webhook-id: <id>

   { "id": 123, "note": "hello" }
   ```
2. Attacker resends the identical raw body/HMAC but changes only the shop header:
   ```
   POST /webhooks
   shopify-topic: orders/create
   shopify-hmac-sha256: <same-valid-signature-over-same-raw-body>
   shopify-shop-domain: victim-shop.myshopify.com
   shopify-webhook-id: <id>

   { "id": 123, "note": "hello" }
   ```
3. `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-31`) succeeds because it only checks the raw body against the shared `api_secret_key`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches to the app's handler with `shop: "victim-shop.myshopify.com"`, even though the payload never originated from that shop.

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
