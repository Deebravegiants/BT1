### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw HTTP body via HMAC, while the `shop` (and `topic`, `webhook_id`, `api_version`) values — which are trusted by host applications to identify *which tenant* a webhook belongs to — are read from unauthenticated headers that fall completely outside the HMAC-covered bytes. This breaks the binding `HMAC(bytes verified) == identity(fields acted on)`, allowing an unprivileged internet user who can obtain any single valid `(raw_body, hmac)` pair to replay it against the app's public webhook endpoint with an arbitrary victim `shop-domain` header and have the gem accept it as authentic.

### Finding Description
The identity binding that should hold is:
`bytes covered by HMAC == bytes/fields the application acts on for tenant identification`

In this gem that equality is broken:

- `to_signable_string` for a webhook `Request` returns **only** the raw body: [1](#0-0) 

- `shop`, `topic`, `webhook_id`, and `api_version` are parsed straight out of HTTP headers, entirely independent of the signed content: [2](#0-1) 

- `HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (i.e., the raw body) against the supplied `hmac`, never touching the headers: [3](#0-2) 

- `Registry.process` performs this HMAC check and, on success, immediately constructs `WebhookMetadata` using the unauthenticated `request.shop` header and hands it to the host app's handler: [4](#0-3) 

- `WebhookMetadata.shop` is the field host applications rely on to determine which merchant/tenant the webhook data belongs to: [5](#0-4) 

Because the HMAC only proves "this body byte-string was produced with the api_secret_key at some point for some shop" and never proves "…for this shop," an attacker who legitimately installs the same public app on their own shop (a fully unprivileged action requiring no leaked credentials) can trigger a webhook whose body they substantially control (e.g., `products/update` with an attacker-chosen title/description that ends up serialized in the JSON body). Shopify will sign that body with the real `api_secret_key`, producing a genuinely valid `(raw_body, hmac)` pair. The attacker then replays this exact body+hmac to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` succeeds (it never looked at the shop header), and `Registry.process` calls the host app's handler with `data.shop == victim_shop` and `data.body == attacker_controlled_content`.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the gem allows an attacker with no privileged credentials to make the host application believe attacker-controlled webhook data originated from a shop the attacker does not control. Depending on how the host app consumes `data.shop`/`data.body` (e.g., updating per-shop billing state, product catalogs, order records, or uninstall/GDPR flags keyed by `shop`), this enables cross-tenant data corruption or spoofed state transitions for a shop the attacker never authenticated as — matching the "cross-tenant access" impact category, since the trust boundary between tenants is defeated using only the gem's own (mis)design, not a host-application bug.

### Likelihood Explanation
Likelihood is high for any app builder relying on `ShopifyAPI::Webhooks::Registry`/`Request` as documented: the webhook HTTP endpoint is by design internet-reachable and unauthenticated aside from the HMAC check (see `docs/usage/webhooks.md`), the attacker only needs to install the (often public) app on a shop they control to legitimately mint a valid `(body, hmac)` pair, and no access token, `client_secret`, or other privileged credential is ever required — only replaying an HTTP POST with a modified header.

### Recommendation
Bind the tenant-identifying headers into the signed material that `HmacValidator` verifies, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the HMAC (e.g., include them in `to_signable_string`, or cross-check `shop` against a value obtained from a source Shopify itself signs, such as validating the webhook against the shop's own known secret/session rather than trusting the header verbatim).

### Proof of Concept
1. Attacker installs the public app on `attacker-shop.myshopify.com` and triggers a `products/update` webhook whose body contains attacker-chosen JSON content in a field like `title`.
2. Shopify sends this webhook to the app's registered endpoint with a genuine `x-shopify-hmac-sha256` computed by `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, raw_body)` — see `lib/shopify_api/utils/hmac_validator.rb:33-40` — over the raw body.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256`, then sends a new POST directly to the app's public webhook route with the same `raw_body`/`hmac` but `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`); `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/utils/hmac_validator.rb:12-22`).
5. The host app's handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker JSON>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), processing attacker-controlled data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
