### Title
Webhook `shop` field is not covered by the HMAC signature, enabling cross-tenant spoofing via `ShopifyAPI::Webhooks::Registry.process` - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported bug class is an inverted/incomplete authorization check that lets an attacker-controlled value slip through unregistered ("bool check wrong ... pool will never be registered" — a value used for a critical decision is not properly bound/verified). The closest reachable analog in `shopify-api-ruby` is in the webhook-verification path: `ShopifyAPI::Utils::HmacValidator` only signs the raw request body, while `ShopifyAPI::Webhooks::Request#shop` is read from an HTTP header that is never included in the signed material. The library nonetheless treats this header as authoritative and hands it straight to the merchant's webhook handler through `WebhookMetadata`, breaking the intended binding `hmac-verified bytes == data acted upon`.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) [2](#0-1) 

`to_signable_string` (the material that `HmacValidator` signs/verifies) is only `@raw_body`: [3](#0-2) 

`shop` is not part of that signed string — it is read straight off the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the HMAC: [4](#0-3) 

`Registry.process` validates only the body HMAC, then immediately forwards the unauthenticated `request.shop` to the app's handler, including for the mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`): [5](#0-4) [6](#0-5) 

The identity binding the library implicitly promises is:
```
hmac_valid(raw_body) == true  =>  (topic, shop, body) can be trusted as an atomic, Shopify-issued unit
```
What is actually verified is only:
```
hmac_valid(raw_body) == true  =>  raw_body was signed with our client_secret
```
`shop` (and `topic`) are excluded from the equality, so any bytes+HMAC pair the attacker can legitimately obtain (e.g., from a webhook fired to their *own* installed shop) can be replayed against the app's public webhook endpoint with an arbitrary `shop-domain` header, and it will pass `HmacValidator.validate` and be dispatched to the handler as if it came from a different, victim shop.

### Impact Explanation
This crosses a tenant boundary without needing `api_secret_key`, an access token, TLS interception, or a privileged account: any user who installs the app on their own store is a legitimate, unprivileged source of a genuinely-signed `(raw_body, hmac)` pair (for example by triggering their own `shop/redact` webhook via app uninstall). They can then POST that same body/HMAC to the app's webhook route with the `shop-domain` header rewritten to a victim's shop. Because the gem does not bind `shop` into the signed payload, `WebhookMetadata#shop` handed to app code is indistinguishable from a legitimate Shopify-attested value, enabling cross-tenant data manipulation (e.g., redaction/deletion logic keyed off `data.shop` for a shop the attacker never installed on) — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Moderate-to-high: no secrets, no interception, and no privileged role are required — only the ability to install the app on an attacker-owned store (a normal, unprivileged action) and send an arbitrary HTTP request to the app's public webhook callback URL, which is required by design to be internet-reachable.

### Recommendation
Include the shop domain (and topic) inside the HMAC-signed material, or otherwise cryptographically bind them (e.g., re-derive the signature over `shop|topic|raw_body`), and reject webhooks where the header-provided `shop` cannot be corroborated against a known/registered shop for that specific `(topic, hmac)` pair before invoking the handler in `ShopifyAPI::Webhooks::Registry.process`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`.
2. Trigger the mandatory `shop/redact` (or any subscribed) webhook against the attacker's own endpoint/log, capturing the raw POST body and its `x-shopify-hmac-sha256` header — both are legitimately produced by Shopify using the app's real `client_secret`.
3. Replay the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` succeeds (it only checks `raw_body` against the secret), and `ShopifyAPI::Webhooks::Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: ..., body: ...)`, as shown in: [5](#0-4) 
5. Any handler logic keyed off `data.shop` (e.g., look up victim's record and redact/delete) is executed against the victim tenant despite the request never actually originating from Shopify on the victim's behalf.

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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
