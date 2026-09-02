This confirms the finding: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, while `Request#shop` reads directly from the `x-shopify-shop-domain` header, which is not included in the HMAC-signed content at all.

### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body [1](#0-0) . The `shop` value handed to the app's handler is read from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, but that header is never part of the HMAC-signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only, and `Webhooks::Request#shop` is derived independently from a header value that is not incorporated into that signable string: [2](#0-1) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., just the raw body) and compares it against the `hmac` header: [3](#0-2) 

`Registry.process` trusts this HMAC check as proof of authenticity for the whole request, then forwards `request.shop` — an unverified field — straight to the app's handler as the tenant identifier: [1](#0-0) 

This breaks the intended binding: `HMAC-verified content == (body, shop)`. In reality the equality is only `HMAC-verified content == body`; `shop` is an independent, unauthenticated header value that can be swapped freely without invalidating the signature, exactly analogous to the reported bug class where a value used to drive a privileged action is not bound to the piece of data that was actually verified.

### Impact Explanation
Because `shop` is not bound to the HMAC, anyone who can obtain one legitimate, validly-signed webhook body+HMAC pair (e.g., by installing the app on their own free/dev store and receiving a real webhook for their own shop) can replay that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. `Registry.process` will still consider the HMAC valid (since it only checks the body) and will invoke the handler with `data.shop` set to the attacker-chosen shop domain, and `data.body` containing attacker-influenced content from their own store. Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's records to update, look up sessions, or otherwise scope database writes (a pattern the gem's own documentation encourages, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be tricked into attributing attacker-supplied data to a victim shop — a cross-tenant data-integrity/confusion issue reachable by an unauthenticated internet user with no access token or secret required.

### Likelihood Explanation
Any user can register their own store, install any app that publicly documents its webhook URL structure, and observe legitimate webhook deliveries (body + `hmac-sha256` header) for topics/fields they control (e.g. `products/update`, `orders/create` on their own dev store). Replaying that captured request to the app's public webhook endpoint with a modified `shop-domain` header requires no secret material and no privileged access — only standard HTTP tooling. The precondition (capturing one's own legitimate webhook) is trivial to satisfy for any app that accepts installs from arbitrary shops (e.g. free listed apps), making this a directly reachable path.

### Recommendation
Include the shop domain (and ideally the webhook `topic`/`webhook-id`) as part of the signed content that is verified, or alternatively require the caller (the host app) to independently verify that `data.shop` corresponds to a shop for which this app has an active installation before trusting it as a scoping key for tenant data. At minimum, the gem should document prominently that `WebhookMetadata#shop` is not itself HMAC-authenticated and must not be trusted for tenant selection without additional verification (e.g. cross-checking against a known list of installed shops).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g. `products/update`) for a topic the app subscribes to.
2. Attacker captures the raw POST body and the `x-shopify-hmac-sha256` header from that legitimate delivery (both are sent to the app's own endpoint, which the attacker controls if they run their own listener, or can otherwise observe if their app receives webhooks at an endpoint they inspect).
3. Attacker replays that identical body and `hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Webhooks::Request.new` accepts the request (all required headers present) [4](#0-3) ; `HmacValidator.validate` succeeds because it only hashes `@raw_body`, unaffected by the header substitution [5](#0-4) .
5. `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker's own webhook body>, ...)` [6](#0-5) , causing the host app to process attacker-controlled data under the victim's tenant identity.

### Citations

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
