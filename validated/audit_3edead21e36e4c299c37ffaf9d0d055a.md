Confirmed: `Registry.process` only validates the HMAC over the raw body via `Utils::HmacValidator.validate(request)` [1](#0-0) , and `Request#to_signable_string` returns only `@raw_body`, never mixing in the `shop-domain` header [2](#0-1) . The `shop` value handed to the app's handler comes straight from an attacker-controllable HTTP header with no cross-check against the HMAC-covered bytes.

### Title
Webhook `shop` (tenant) identity is not bound to the HMAC-verified payload, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by recomputing an HMAC over the raw request body and comparing it to the `X-Shopify-Hmac-Sha256`/`shopify-hmac-sha256` header [3](#0-2) . The `shop` attribute that is subsequently handed to the application's `WebhookHandler` is read directly from the unauthenticated `shop-domain` header and is never included in the signed material [4](#0-3) [5](#0-4) . Since the HMAC secret (`api_secret_key`) is a single **app-level** secret shared across every merchant that installs the app, any signature that is valid for one shop's webhook body is equally valid for the same body claimed to originate from a different shop.

### Finding Description
The identity binding that should hold is:
`shop_that_HMAC-authenticated_data_belongs_to == shop_header_value_used_by_the_handler`

In this gem that equality is never checked:
- `Request#hmac` and `Request#to_signable_string` only look at the request body [6](#0-5) .
- `Request#shop` simply reads the `shopify-shop-domain`/`x-shopify-shop-domain` header with no verification [4](#0-3) .
- `Registry.process` validates the HMAC, then immediately builds `WebhookMetadata` using `request.shop` taken from that same unauthenticated header, with no cross-check that the body's HMAC and the claimed shop are consistent [1](#0-0) .

Because the webhook endpoint is a public HTTP endpoint (no other authentication is documented or enforced for receiving webhooks; see `docs/usage/webhooks.md`), any unprivileged internet user who can obtain one genuinely-signed `(raw_body, hmac)` pair — for example by installing the target app on their own free/trial development shop and capturing a real webhook call the app sends to itself — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` will report success (it only checks the body against the app-wide secret) [7](#0-6) , and the handler will process attacker-controlled data as if it were an authentic event for the victim shop.

### Impact Explanation
This crosses a tenant boundary without any of the excluded prerequisites (no access token, no `api_secret_key`, no privileged account is required by the attacker). Depending on the topic handled, this enables cross-tenant data confusion/injection attributed to a victim shop — e.g. spoofing `app/uninstalled` to trigger deletion of a victim's stored session/data, or spoofing an order/customer webhook to inject attacker-chosen data tagged as belonging to the victim shop. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only: (1) ability to install the target app on any shop (trivial, since installable apps are generally open to any merchant/dev store), (2) capturing one legitimate webhook delivery from that shop to observe a valid `(body, hmac)` pair, and (3) sending a crafted HTTP POST to the app's public webhook endpoint with a different `shop-domain` header. No secrets, tokens, or social engineering needed.

### Recommendation
Bind the claimed shop to the authenticated payload before dispatching to handlers, e.g.:
- Include the `shop-domain` (and ideally `webhook-id`/`api-version`) header values in the HMAC-signed material used by `Request#to_signable_string`, or
- Require the caller to independently verify that `request.shop` corresponds to a shop with a known, stored session/access token for this app before invoking `handler.handle`, and document this as a mandatory step rather than leaving it entirely to the host application.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they control) and triggers a webhook (e.g. `app/uninstalled`, which typically has an empty or minimal body `{}`).
2. Attacker captures the genuine POST request Shopify sent, including headers `shopify-hmac-sha256: <valid signature over "{}" using the app's api_secret_key>` and `shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker crafts a new POST to the app's public webhook endpoint with the identical body `{}` and identical `shopify-hmac-sha256` value, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses the request; `Utils::HmacValidator.validate` recomputes the HMAC over `"{}"` and finds it matches (the secret is shared across all shops) [8](#0-7) .
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:..., shop: "victim-shop.myshopify.com", ...))` [9](#0-8) , causing the app to act on victim-shop's tenant record using attacker-supplied event data, despite the victim never having sent this webhook.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L27-31)
```ruby
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
