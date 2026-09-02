### Title
Webhook shop-domain header is trusted for tenant attribution but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`/`webhook_id`) values that the gem hands to the app's handler as the tenant identifier are read straight from HTTP headers and are never included in the signed bytes. Anyone who possesses one validly-signed webhook body/HMAC pair (e.g., a webhook Shopify legitimately delivered for their own shop) can replay that exact body+HMAC while substituting a different `shopify-shop-domain` header, and `Registry.process` will accept it as authentic and hand the attacker-chosen shop to the app's handler.

### Finding Description
`Webhooks::Request#hmac`/`#to_signable_string` expose only the raw body as the signable content: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are parsed from headers, entirely outside the signable string: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac-sha256` header — it performs no binding check between the signature and `request.shop`/`request.topic`/`request.webhook_id`: [3](#0-2) [4](#0-3) 

The unauthenticated `shop` value is then forwarded as the tenant identifier to the host application's handler via `WebhookMetadata`: [5](#0-4) 

This is the same class of bug as the report: an identity field ("shop", the tenant key) that is *acted upon* (used to construct `WebhookMetadata.shop`, which apps commonly use as a database key to look up/act on that merchant's session, records, or access token) is not covered by the cryptographic check that gates acceptance of the request. The equality that should hold is:

`shop_used_for_tenant_attribution == shop_bound_by_signature`

but in fact:

`shop_used_for_tenant_attribution (header, attacker-controlled) != shop_bound_by_signature (never signed — signature covers body bytes only)`

Any party that has received one legitimately signed webhook delivery for their own shop (a completely unprivileged event — every merchant that installs the app receives such webhooks) can capture `(raw_body, hmac_header)` and replay it to the app's public webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop. `HmacValidator.validate` recomputes the same signature over the same body and succeeds, so `Registry.process` treats the forged shop as authentic and invokes the app's handler with `WebhookMetadata.shop` set to the victim's domain.

### Impact Explanation
This breaks the tenant boundary between shops: an attacker who only has access to their own shop's legitimate webhook traffic can impersonate a different, victim shop's webhook stream to the app, because the app's own trust boundary (`Registry.process`) does not bind `shop` to the signature. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` (commonly to look up the corresponding merchant session/access token or write into that merchant's records), this enables cross-tenant data corruption or triggering privileged app logic under a victim shop's identity. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app: obtaining a valid `(body, hmac)` pair requires no privileged access — merely having the app installed on any shop (the attacker's own) is enough to receive a legitimate webhook with a valid signature computed with the app's shared `client_secret`. Because the HMAC is a single shared secret across all shops using the app (not per-shop), the signature by design proves only "signed by this app's secret," not "originated for shop X." No `api_secret_key`, access token, or social engineering is required — only observing traffic the attacker is already entitled to receive.

### Recommendation
Do not treat header-derived `shop`/`topic`/`webhook_id` as authenticated. Either:
- Include `shop`, `topic`, and `webhook_id` in the signed payload/signable string so the HMAC binds them, or
- Require the host application to independently verify that the claimed `shop` corresponds to a shop that has an active installation/session for this app before trusting `WebhookMetadata.shop`, and document this requirement prominently, or
- Reject webhooks where the claimed shop domain has not been separately confirmed (e.g., cross-check against Shopify's webhook delivery source or a per-shop webhook registration record) rather than accepting body-HMAC validity alone as proof of shop identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and lets Shopify deliver a real webhook (e.g. `orders/create`) to the app's registered endpoint. They capture the full raw body `B` and the `X-Shopify-Hmac-Sha256` header `H` for this delivery — a signature computed by Shopify using the app's shared `client_secret`, valid per `HmacValidator.validate`.
2. Attacker sends a new POST to the same app webhook endpoint containing the identical raw body `B` and identical `hmac-sha256` header `H`, but with the `shopify-shop-domain` header changed to `victim-shop.myshopify.com` (and, if desired, an arbitrary `shopify-webhook-id`/`shopify-topic` chosen to route to a specific handler).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (header presence checks pass) [6](#0-5) .
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and successfully matches `H`, so validation passes [3](#0-2) .
5. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [7](#0-6) , causing the app to act as though the event legitimately originated from the victim shop.

### Citations

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
