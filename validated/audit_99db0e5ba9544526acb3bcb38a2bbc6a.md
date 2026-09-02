This confirms the analog. The webhook HMAC in `ShopifyAPI::Webhooks::Request` only signs the raw body (`to_signable_string` returns `@raw_body`), while the `shop`, `topic`, `api_version`, and `webhook_id` fields are all read directly from unauthenticated HTTP headers via `shopify_header`. `Registry.process` validates the HMAC against the body only, then passes the header-derived `request.shop` straight into the handler as trusted tenant identity. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant request forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` authenticates the byte content of the POST body but never binds the `shop-domain` header (nor `topic`, `api_version`, `webhook_id`) to that signature. `Registry.process` trusts `request.shop`, taken straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, and hands it to the app's webhook handler as the tenant identity for the delivered body.

### Finding Description
The verification contract for webhooks is: "the bytes verified by HMAC == the bytes the handler acts on." That equality breaks here because only the request body is verified:

- `hmac` is computed by Shopify over `raw_body` and validated the same way locally: [5](#0-4)  and [2](#0-1) .
- `shop` is parsed purely from the HTTP header, independent of the signed content: [1](#0-0) .
- `Registry.process` validates only the HMAC-covered body, then constructs `WebhookMetadata` using the unauthenticated `request.shop`: [3](#0-2) .

Because Shopify signs webhook deliveries with a secret shared across every shop that installs the app (the app's `client_secret`/webhook signing secret, not a per-shop secret), any given signed `(body, hmac)` pair recorded from one legitimate delivery — e.g., from the attacker's own installed shop — remains a valid HMAC for that same body regardless of which `shop-domain` header accompanies it. An attacker who controls a shop installing the app (a normal, unprivileged action) can capture a legitimate webhook delivery from their own store, then replay the identical body/hmac to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. `Utils::HmacValidator.validate` will still return `true` because it only re-derives the HMAC over `raw_body`, and the handler will process attacker-supplied body content attributed to the victim's shop.

### Impact Explanation
This breaks the tenant/shop identity binding at the trust boundary between "bytes Shopify signed" and "shop the handler believes it received data for" — a cross-tenant confusion. If a host application's webhook handler uses `data.shop` (sourced from `WebhookMetadata`) to select per-tenant records, sessions, or perform per-tenant side effects (a documented and expected usage pattern, since `WebhookMetadata#shop` is the library's exposed API for this purpose), an attacker can inject attacker-controlled webhook payloads that are misattributed to a victim shop, since the shop label itself carries no cryptographic binding. This matches the "Critical – cross-tenant access" impact category, since it lets an unprivileged, but authenticated-as-a-different-shop, attacker forge webhook events under another tenant's identity.

### Likelihood Explanation
Low-to-moderate: it requires the attacker to operate their own shop installation of the app (a normal, freely available action for any Shopify merchant) to obtain one validly-signed `(body, hmac)` pair, then send a forged HTTP request to the app's webhook endpoint with a spoofed `shop-domain` header. No access token, `client_secret`, or privileged account is needed — only the ability to install the app on any shop and to send arbitrary HTTP requests to the app's public webhook callback URL.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the signable string used for HMAC verification, or otherwise cryptographically bind them to the request body before trusting `request.shop` — e.g., verify HMAC over a canonical string that concatenates `shop-domain` with `raw_body`, or independently corroborate the header-derived shop against a value embedded in the signed payload. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used by host applications for tenant-sensitive authorization decisions without additional verification.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent (this is a validly signed `(body, hmac)` pair for the app's shared webhook secret).
2. Send a new HTTP POST to the app's webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` header captured in step 1, but replace `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the raw body only) and finds it matches, since the body and hmac are untouched. [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, achieving cross-tenant request forgery. [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
